# Neo4j ↔ Tavily Integration Schema Design

**Complete 4-Phase Integration**: Caching → Effectiveness → Semantic Search → User Feedback

---

## Phase 1: Tavily Result Caching

### Node Structure

#### TavilyCache Node
```cypher
(:TavilyCache {
  query_hash: String,        // SHA-256 hash of normalized query (index key)
  original_query: String,    // Original user query for debugging
  created_at: DateTime,      // When cache entry was created
  expires_at: DateTime,      // When cache entry expires (TTL)
  results_count: Integer,    // Number of results cached
  results_json: String       // JSON string of Tavily API response
})
```

**Why JSON String?**
- Neo4j doesn't natively support nested arrays/objects
- Easier to deserialize entire Tavily response
- Preserves exact API structure for compatibility

**TTL Strategy**:
- Documentation: 7 days (docs don't change frequently)
- Tutorial content: 7 days
- API references: 7 days
- News/blog posts: 3 days (if we add later)

### Indexes

```cypher
// Fast lookup by query hash
CREATE INDEX tavily_cache_hash_idx FOR (n:TavilyCache) ON (n.query_hash);

// Cleanup expired entries
CREATE INDEX tavily_cache_expires_idx FOR (n:TavilyCache) ON (n.expires_at);
```

### Query Normalization

To maximize cache hits, normalize queries before hashing:

```python
def normalize_query(query: str) -> str:
    """
    Normalize query for consistent cache keys

    Examples:
      "Build React app" → "build react app"
      "  Create REACT APP  " → "create react app"
      "Build React application" → "build react application" (different!)
    """
    return query.lower().strip()
```

**Trade-off**: Simple normalization (lowercase + trim) vs semantic similarity
- **Phase 1**: Simple normalization (exact match only)
- **Phase 3**: Semantic similarity (find related cached queries)

### Cache Operations

#### 1. Cache Write (after Tavily API call)

```cypher
MERGE (cache:TavilyCache {query_hash: $query_hash})
SET cache.original_query = $original_query,
    cache.created_at = datetime(),
    cache.expires_at = datetime() + duration({days: $ttl_days}),
    cache.results_count = $results_count,
    cache.results_json = $results_json
RETURN cache.query_hash as hash
```

#### 2. Cache Read (before Tavily API call)

```cypher
MATCH (cache:TavilyCache {query_hash: $query_hash})
WHERE cache.expires_at > datetime()  // Only return fresh results
RETURN cache.results_json as results,
       cache.created_at as cached_at,
       cache.results_count as count
```

#### 3. Cache Cleanup (periodic maintenance)

```cypher
// Delete expired entries
MATCH (cache:TavilyCache)
WHERE cache.expires_at <= datetime()
DELETE cache
RETURN count(cache) as deleted_count
```

## Phase 2: Documentation Effectiveness Tracking

### Node Structure

#### Documentation Node
```cypher
(:Documentation {
  url: String,              // Unique identifier (index key)
  title: String,            // Document title from Tavily
  domain: String,           // Extracted domain (e.g., "react.dev")
  first_seen: DateTime,     // When first encountered
  last_seen: DateTime,      // Most recent use
  total_uses: Integer       // Total times used across all patterns
})
```

### Relationship Structure

#### CONTRIBUTED_TO Relationship
```cypher
(:Documentation)-[:CONTRIBUTED_TO {
  galileo_score: Float,     // Quality score when this doc was used
  used_at: DateTime,        // When this doc contributed to pattern
  agent: String             // Which agent used it ("architecture", "implementation")
}]->(:Pattern)
```

**Why track agent?**
- Learn which docs help Architecture vs Implementation
- Some docs might be great for planning, poor for coding

### Indexes

```cypher
// Fast lookup by URL
CREATE INDEX doc_url_idx FOR (n:Documentation) ON (n.url);

// Find docs by domain
CREATE INDEX doc_domain_idx FOR (n:Documentation) ON (n.domain);

// Sort by effectiveness
CREATE INDEX doc_uses_idx FOR (n:Documentation) ON (n.total_uses);
```

### Effectiveness Queries

#### Get Top Performing Docs

```cypher
MATCH (d:Documentation)-[r:CONTRIBUTED_TO]->(p:Pattern)
WITH d,
     count(r) as use_count,
     avg(r.galileo_score) as avg_score,
     stdDev(r.galileo_score) as score_stddev
WHERE use_count >= 3  // Minimum sample size
RETURN d.url as url,
       d.title as title,
       d.domain as domain,
       use_count,
       avg_score,
       score_stddev
ORDER BY avg_score DESC, use_count DESC
LIMIT 10
```

#### Get Docs for Specific Domain

```cypher
MATCH (d:Documentation {domain: $domain})-[r:CONTRIBUTED_TO]->(:Pattern)
WITH d, avg(r.galileo_score) as avg_score, count(r) as uses
RETURN d.url, d.title, avg_score, uses
ORDER BY avg_score DESC
```

## Phase 3: Semantic Documentation Search

### Extended Schema

#### Task Embedding (for similarity search)

```cypher
(:Pattern {
  // Existing fields...
  task_keywords: [String],       // Extracted keywords from task
  task_embedding: [Float]        // Optional: Vector embedding (future)
})
```

**Keyword Extraction**:
```python
def extract_keywords(task: str) -> List[str]:
    """
    Extract key technical terms from task

    "Build React app with hooks and routing"
    → ["react", "hooks", "routing", "app"]
    """
    import re
    # Remove common words
    stopwords = {"build", "create", "make", "with", "and", "the", "a"}
    words = re.findall(r'\b\w+\b', task.lower())
    return [w for w in words if w not in stopwords and len(w) > 2]
```

### Proven Docs Query

```cypher
// Find docs that worked well for similar tasks
MATCH (p:Pattern)
WHERE any(kw IN $keywords WHERE kw IN p.task_keywords)

// Get docs used in those patterns
MATCH (d:Documentation)-[r:CONTRIBUTED_TO]->(p)

// Calculate effectiveness
WITH d,
     avg(r.galileo_score) as avg_score,
     count(r) as uses,
     collect(p.task) as similar_tasks
WHERE avg_score >= $min_score AND uses >= 2

RETURN d.url,
       d.title,
       avg_score,
       uses,
       similar_tasks[0..3] as sample_tasks  // Show example tasks
ORDER BY avg_score DESC, uses DESC
LIMIT $limit
```

## Complete Graph Model

```
                  ┌─────────────┐
                  │ TavilyCache │
                  │   (Phase 1) │
                  └─────────────┘
                        ↓
              [Cached Tavily Results]
                        ↓
                  ┌─────────────┐
                  │Documentation│──┐
                  │   (Phase 2) │  │
                  └─────────────┘  │
                        │          │
                  [:CONTRIBUTED_TO]│
                   {score: 96.0}   │
                        ↓          │
                  ┌─────────────┐  │
                  │   Pattern   │←─┘
                  │   (Phase 3) │
                  │ {keywords}  │
                  └─────────────┘
```

## Implementation Notes

### Data Consistency

**Cache Invalidation**:
- Automatic via TTL (expires_at check)
- Manual via cleanup job (run weekly)

**Doc Node Updates**:
```python
# MERGE pattern: Update if exists, create if not
MERGE (d:Documentation {url: $url})
SET d.title = $title,  # Update title if changed
    d.last_seen = datetime(),
    d.total_uses = d.total_uses + 1  # Increment counter
```

### Performance Considerations

**Expected Scale** (after 1000 sessions):
- TavilyCache nodes: ~500 (50% unique queries)
- Documentation nodes: ~2,000 (5 URLs per query avg)
- CONTRIBUTED_TO rels: ~5,000 (2.5 uses per doc avg)

**Query Performance**:
- Cache lookup: <10ms (indexed on query_hash)
- Doc effectiveness: <50ms (aggregation on 5K relationships)
- Proven docs: <100ms (keyword match + aggregation)

### Migration Strategy

**Phase 1 → Phase 2**:
- No migration needed (additive)
- Start tracking docs on new patterns only
- Historical patterns won't have doc links (graceful degradation)

**Phase 2 → Phase 3**:
- Add keywords to existing Pattern nodes via migration:
```cypher
MATCH (p:Pattern)
WHERE p.task_keywords IS NULL
SET p.task_keywords = split(toLower(p.task), ' ')
```

## Testing Strategy

### Phase 1 Tests

```python
# Test 1: Cache miss
assert neo4j.get_cached_tavily_results("React hooks") is None

# Test 2: Cache write
neo4j.cache_tavily_results("React hooks", {...})

# Test 3: Cache hit
cached = neo4j.get_cached_tavily_results("React hooks")
assert cached is not None

# Test 4: Case insensitivity
cached = neo4j.get_cached_tavily_results("REACT HOOKS")
assert cached is not None  # Same hash as "react hooks"

# Test 5: TTL expiration (set to 1 second for testing)
neo4j.cache_tavily_results("Test", {...}, ttl_days=1/86400)
sleep(2)
assert neo4j.get_cached_tavily_results("Test") is None
```

### Phase 2 Tests

```python
# Test 1: Link docs to pattern
neo4j.link_docs_to_pattern(
    pattern_id="pattern_123",
    docs=[{"url": "react.dev/hooks", "title": "React Hooks"}],
    score=96.0
)

# Test 2: Query effectiveness
stats = neo4j.get_doc_effectiveness_stats(min_uses=1)
assert any(d["url"] == "react.dev/hooks" for d in stats)
assert stats[0]["avg_score"] == 96.0
```

### Phase 3 Tests

```python
# Test 1: Keyword extraction
keywords = extract_keywords("Build React app with hooks")
assert "react" in keywords
assert "hooks" in keywords
assert "build" not in keywords  # Stopword

# Test 2: Proven docs retrieval
proven = neo4j.get_proven_docs_for_task("Create React component", min_avg_score=90, limit=3)
assert len(proven) <= 3
assert all(d["avg_score"] >= 90 for d in proven)
```

## Schema Version

**Version**: 1.0.0
**Date**: 2025-10-20
**Author**: CodeSwarm Team
**Status**: Phase 1 Ready for Implementation

---

## Phase 4: User Feedback Loop

**Goal**: Capture user feedback to improve documentation selection and enable retry mechanism

### Node Structure

#### UserFeedback Node
```cypher
(:UserFeedback {
  session_id: String,          // Unique session identifier
  pattern_id: String,          // Link to CodePattern that was generated
  task: String,                // Original user task (for context)
  
  // User ratings (1-5 scale)
  code_quality: Integer,       // "How well did the code meet your needs?"
  context_quality: Integer,    // "Did the documentation seem relevant?"
  
  // Metadata
  timestamp: DateTime,
  would_retry: Boolean,        // Did user request retry with more docs?
  retry_session_id: String     // If retry, link to new session
})
```

### Relationships

#### Documentation Negative Feedback
```cypher
// User explicitly marked a doc as unhelpful
(:Documentation)-[:RECEIVED_NEGATIVE_FEEDBACK {
  session_id: String,
  user_reason: String,          // Why doc didn't help
  timestamp: DateTime
}]->(:UserFeedback)

// Track negative feedback weight for future deprioritization
(:Documentation {
  negative_feedback_count: Integer,
  negative_feedback_rate: Float  // % of uses that got negative feedback
})
```

#### Pattern Feedback Link
```cypher
(:CodePattern)<-[:FEEDBACK_FOR]-(:UserFeedback)
```

### Feedback Collection Flow

```
1. Code generation completes
   ↓
2. CLI prompts user:
   "Rate code quality (1-5): "
   "Rate documentation relevance (1-5): "
   ↓
3. If context_quality < 3:
   "Which docs seemed irrelevant? (comma-separated indices, or 'none')"
   "Would you like to retry with expanded search? (y/n)"
   ↓
4. Store feedback in Neo4j
   ↓
5. If retry requested:
   - Exclude negatively-rated docs
   - Expand Tavily max_results (5 → 10)
   - Re-run full workflow
   - Link retry session to original
```

### Cypher Queries

#### Store User Feedback
```cypher
// Create feedback node
CREATE (f:UserFeedback {
  session_id: $session_id,
  pattern_id: $pattern_id,
  task: $task,
  code_quality: $code_quality,
  context_quality: $context_quality,
  timestamp: datetime(),
  would_retry: $would_retry,
  retry_session_id: $retry_session_id
})

// Link to pattern
WITH f
MATCH (p:CodePattern {id: $pattern_id})
CREATE (f)-[:FEEDBACK_FOR]->(p)

RETURN f.session_id as session_id
```

#### Mark Doc as Unhelpful
```cypher
// Find or create documentation node
MERGE (doc:Documentation {url: $url})
ON CREATE SET
  doc.negative_feedback_count = 0,
  doc.total_uses = 0

// Increment negative feedback counter
SET doc.negative_feedback_count = doc.negative_feedback_count + 1,
    doc.negative_feedback_rate = toFloat(doc.negative_feedback_count) / doc.total_uses

// Link negative feedback
WITH doc
MATCH (f:UserFeedback {session_id: $session_id})
CREATE (doc)-[:RECEIVED_NEGATIVE_FEEDBACK {
  session_id: $session_id,
  user_reason: $reason,
  timestamp: datetime()
}]->(f)

RETURN doc.url, doc.negative_feedback_rate
```

#### Get Docs to Exclude (High Negative Feedback)
```cypher
// Find docs with >30% negative feedback rate
MATCH (doc:Documentation)
WHERE doc.negative_feedback_rate > 0.3
  AND doc.total_uses >= 3  // Min sample size
RETURN doc.url, doc.negative_feedback_rate, doc.negative_feedback_count
ORDER BY doc.negative_feedback_rate DESC
```

### Adaptive Search Strategy

When user requests retry:

```python
# 1. Get excluded docs
excluded_docs = neo4j.get_high_negative_feedback_docs(
    min_negative_rate=0.3,
    min_uses=3
)
excluded_urls = [d["url"] for d in excluded_docs]

# 2. Expand Tavily search
documentation = tavily.search_and_extract_docs(
    task=task,
    max_results=10,  # Doubled from 5
    exclude_domains=[urlparse(u).netloc for u in excluded_urls]
)

# 3. Link retry sessions
neo4j.link_retry_session(
    original_session_id=original_session_id,
    retry_session_id=new_session_id
)
```

### Analytics Queries

#### Overall Satisfaction by Documentation Source
```cypher
MATCH (doc:Documentation)-[:CONTRIBUTED_TO]->(p:CodePattern)<-[:FEEDBACK_FOR]-(f:UserFeedback)
WITH doc.domain as domain,
     avg(f.code_quality) as avg_code_quality,
     avg(f.context_quality) as avg_context_quality,
     count(f) as feedback_count
WHERE feedback_count >= 5
RETURN domain, avg_code_quality, avg_context_quality, feedback_count
ORDER BY avg_context_quality DESC
```

#### Retry Success Rate
```cypher
// Compare original vs retry session scores
MATCH (f1:UserFeedback)-[:TRIGGERED_RETRY]->(f2:UserFeedback)
WITH f1.code_quality as original_quality,
     f2.code_quality as retry_quality,
     f1.context_quality as original_context,
     f2.context_quality as retry_context
RETURN avg(retry_quality - original_quality) as quality_improvement,
       avg(retry_context - original_context) as context_improvement,
       count(*) as retry_count
```

### Indexes

```cypher
// Fast session lookup
CREATE INDEX feedback_session_idx FOR (n:UserFeedback) ON (n.session_id);

// Fast pattern feedback lookup
CREATE INDEX feedback_pattern_idx FOR (n:UserFeedback) ON (n.pattern_id);

// Negative feedback rate filtering
CREATE INDEX doc_negative_rate_idx FOR (n:Documentation) ON (n.negative_feedback_rate);
```

### Testing Phase 4

```python
# Test 1: Store feedback
neo4j.store_user_feedback(
    session_id="session_123",
    pattern_id="pattern_456",
    task="Create React app",
    code_quality=4,
    context_quality=2
)

# Test 2: Mark doc as unhelpful
neo4j.mark_doc_unhelpful(
    url="example.com/bad-doc",
    session_id="session_123",
    reason="Outdated information"
)

# Test 3: Get excluded docs
excluded = neo4j.get_high_negative_feedback_docs(min_negative_rate=0.3)
assert all(d["negative_feedback_rate"] > 0.3 for d in excluded)

# Test 4: Retry session linkage
neo4j.link_retry_session(
    original_session_id="session_123",
    retry_session_id="session_789"
)
```

---

## Schema Version

**Version**: 2.0.0  
**Date**: 2025-10-20  
**Author**: CodeSwarm Team  
**Status**: Phase 1-4 Complete - Ready for Full System Testing
