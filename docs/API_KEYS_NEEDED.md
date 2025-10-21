# API Keys Needed - REAL Integrations Only

##  CRITICAL - Blake Must Provide

### 1. Galileo Observe
- **GALILEO_API_KEY** = ?
- **Where to get**: Galileo dashboard/account
- **Used for**: Real quality evaluation (90+ threshold)
- **Current**: Mock (NOT ACCEPTABLE)
- **Priority**: P0 - MUST HAVE

### 2. Browser Use
- **Package**: `browser-use`
- **API Key needed?**: Check documentation
- **Where to get**: Browser Use service
- **Used for**: Live documentation scraping
- **Current**: Not integrated
- **Priority**: P0 - MUST HAVE

### 3. WorkOS
- **WORKOS_API_KEY** = ?
- **WORKOS_CLIENT_ID** = ?
- **Where to get**: WorkOS dashboard
- **Used for**: Team authentication, SSO
- **Current**: Placeholder values
- **Priority**: P0 - MUST HAVE

### 4. Daytona
- **DAYTONA_API_KEY** = ?
- **DAYTONA_API_URL** = ?
- **DAYTONA_WORKSPACE_ID** = ?
- **Where to get**: Daytona dashboard
- **Used for**: Development workspace, deployment
- **Current**: Placeholder values
- **Priority**: P0 - MUST HAVE

### 5. Neo4j
- **Question**: Do we need Docker for Neo4j?
- **Options**:
  - A) Use Docker locally: `docker compose up -d`
  - B) Use Neo4j Aura (cloud) - need credentials
  - C) Skip and use local file storage
- **Used for**: RAG knowledge base (90+ patterns)
- **Current**: Config in .env but not running
- **Priority**: P0 - MUST HAVE

---

##  Already Have (Working)

### OpenRouter
- **OPENROUTER_API_KEY** = sk-or-v1-539... 
- **Status**: WORKING (tested successfully)
- **Provides**: Claude Sonnet 4.5, GPT-5 Pro, Grok-4, all models

### OpenAI
- **OPENAI_API_KEY** = sk-proj-5Crav... 
- **Status**: Available (backup)

### Weights & Biases (Weave)
- **WANDB_API_KEY** = c1e3ac... 
- **Status**: Available for observability

---

##  Blake's Action Items

Please provide:

1. **Galileo API Key**
   ```bash
   GALILEO_API_KEY=<your-key-here>
   ```

2. **Browser Use Setup**
   - API key (if needed)
   - Installation instructions
   - Documentation link

3. **WorkOS Credentials**
   ```bash
   WORKOS_API_KEY=<your-key-here>
   WORKOS_CLIENT_ID=<your-client-id>
   ```

4. **Daytona Credentials**
   ```bash
   DAYTONA_API_KEY=<your-key-here>
   DAYTONA_API_URL=<api-url>
   DAYTONA_WORKSPACE_ID=<workspace-id>
   ```

5. **Neo4j Decision**
   - [ ] Option A: I'll spin up Docker locally
   - [ ] Option B: Use Neo4j Aura cloud (provide credentials)
   - [ ] Option C: Use file-based storage (no Neo4j)

---

##  NO MOCKS ALLOWED

Current mock implementations to REMOVE:
-  Mock Galileo evaluator in `src/evaluation/galileo_evaluator.py`
-  Any simulated scoring
-  Fake data generators

Everything must use REAL APIs.

---

## ⏱ How Long Will This Take?

Once Blake provides keys:
- Galileo integration: 30 min
- Browser Use integration: 45 min
- WorkOS integration: 60 min
- Daytona integration: 60 min
- Neo4j setup: 30 min (Docker) or 20 min (cloud)

**Total: ~4 hours of integration work**

---

##  Next Steps

1. Blake provides all API keys above
2. I remove ALL mock code
3. I integrate each service properly with real APIs
4. We test end-to-end with REAL integrations
5. Demo will show ACTUAL sponsor tools working

**Waiting for Blake to provide API credentials...**
