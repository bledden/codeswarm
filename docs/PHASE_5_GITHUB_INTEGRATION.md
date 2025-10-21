# Phase 5: GitHub Integration - Design Document

## Overview

Add GitHub repository creation and push functionality to the user feedback loop, allowing users to commit their generated code directly to GitHub after generation completes.

---

## User Flow

```
1. Code generation completes
   ↓
2. User provides feedback (Phase 4)
   ↓
3. CLI asks: "Would you like to push this to GitHub? (y/n)"
   ↓
4. If yes:
   a. Check for GitHub authentication
   b. If not authenticated → OAuth flow via MCP or GitHub App
   c. Ask for repo name
   d. Initialize git repo locally
   e. Create GitHub repository
   f. Push code to GitHub
   g. Return GitHub URL
   ↓
5. Store GitHub URL in Neo4j linked to pattern
```

---

## Implementation Options

### Option 1: GitHub MCP Server (Recommended)

Use the official [GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github) for standardized GitHub operations.

**Pros**:
- Official MCP implementation
- Handles OAuth automatically
- Standardized across all MCP-compatible tools
- Supports repositories, issues, PRs, search

**Cons**:
- Requires MCP server setup
- Additional dependency

**MCP Tools Available**:
```json
{
  "create_repository": {
    "name": "string",
    "description": "string",
    "private": "boolean"
  },
  "push_files": {
    "owner": "string",
    "repo": "string",
    "files": [{"path": "string", "content": "string"}],
    "message": "string",
    "branch": "string"
  }
}
```

### Option 2: GitHub OAuth + PyGithub

Direct GitHub integration using OAuth flow and PyGithub library.

**Pros**:
- No MCP dependency
- Full control over OAuth flow
- Familiar GitHub API

**Cons**:
- Manual OAuth implementation
- More code to maintain

### Option 3: GitHub CLI (gh) via Subprocess

Use GitHub CLI commands via subprocess.

**Pros**:
- Simple implementation
- Users already have `gh` installed (likely)

**Cons**:
- Requires `gh` CLI installed
- Less control over errors
- Subprocess overhead

---

## Recommended Architecture: MCP-First with GitHub CLI Fallback

```python
# 1. Try MCP server first (if configured)
if mcp_github_server_available:
    result = mcp_github.create_and_push(...)

# 2. Fall back to GitHub CLI
elif gh_cli_available:
    result = subprocess.run(['gh', 'repo', 'create', ...])

# 3. Fall back to manual instructions
else:
    print("Install GitHub CLI or configure MCP server")
    print("Manual: https://github.com/new")
```

---

## Schema Extension

### Neo4j Schema

```cypher
// Add GitHub URL to CodePattern
(:CodePattern {
  github_url: String,          // Optional: GitHub repo URL
  github_pushed_at: DateTime,  // When code was pushed
  github_repo_name: String     // Repo name (e.g., "user/repo")
})

// Track GitHub pushes
(:CodePattern)-[:PUSHED_TO_GITHUB {
  url: String,
  pushed_at: DateTime,
  commit_sha: String,          // Initial commit SHA
  branch: String               // Usually "main"
}]->(:GitHubRepository {
  url: String,
  owner: String,
  repo: String,
  created_at: DateTime,
  is_private: Boolean
})
```

### Analytics Queries

```cypher
// GitHub push rate
MATCH (p:CodePattern)
WITH count(p) as total_patterns,
     count(p.github_url) as pushed_patterns
RETURN (toFloat(pushed_patterns) / total_patterns) * 100 as push_rate_percent

// Most pushed project types
MATCH (p:CodePattern)-[:PUSHED_TO_GITHUB]->(g:GitHubRepository)
RETURN p.task, count(*) as push_count
ORDER BY push_count DESC
LIMIT 10
```

---

## Implementation Steps

### Step 1: Add GitHub Client

```python
# src/integrations/github_client.py

from typing import Optional, Dict, Any
import subprocess
import os

class GitHubClient:
    """
    GitHub integration for CodeSwarm

    Supports:
    1. MCP GitHub Server (primary)
    2. GitHub CLI (fallback)
    3. Manual instructions (last resort)
    """

    def __init__(self, use_mcp: bool = True):
        self.use_mcp = use_mcp
        self.gh_cli_available = self._check_gh_cli()

    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is installed and authenticated"""
        try:
            result = subprocess.run(
                ['gh', 'auth', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def create_and_push_repo(
        self,
        repo_name: str,
        description: str,
        files: Dict[str, str],
        is_private: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create GitHub repository and push generated code

        Args:
            repo_name: Repository name
            description: Repository description
            files: Dict of filename -> content
            is_private: Whether repo should be private

        Returns:
            {
                "url": "https://github.com/user/repo",
                "owner": "user",
                "repo": "repo",
                "commit_sha": "abc123..."
            }
        """
        # Try MCP first
        if self.use_mcp:
            try:
                return await self._create_via_mcp(
                    repo_name, description, files, is_private
                )
            except Exception as e:
                print(f"  ⚠️  MCP failed: {e}, trying GitHub CLI...")

        # Fall back to GitHub CLI
        if self.gh_cli_available:
            return await self._create_via_gh_cli(
                repo_name, description, files, is_private
            )

        # Manual instructions
        print("  ❌ GitHub CLI not installed")
        print(f"  📋 Manual: Create repo at https://github.com/new")
        print(f"     Name: {repo_name}")
        print(f"     Description: {description}")
        return None

    async def _create_via_gh_cli(
        self,
        repo_name: str,
        description: str,
        files: Dict[str, str],
        is_private: bool
    ) -> Dict[str, Any]:
        """Create repo using GitHub CLI"""
        import tempfile
        import shutil

        # Create temp directory for git operations
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write files
            for filename, content in files.items():
                filepath = os.path.join(tmpdir, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w') as f:
                    f.write(content)

            # Git init
            subprocess.run(['git', 'init'], cwd=tmpdir, check=True)
            subprocess.run(['git', 'add', '.'], cwd=tmpdir, check=True)
            subprocess.run([
                'git', 'commit', '-m',
                '🐝 Generated by CodeSwarm\n\nCo-Authored-By: Claude <noreply@anthropic.com>'
            ], cwd=tmpdir, check=True)

            # Create GitHub repo
            visibility = '--private' if is_private else '--public'
            result = subprocess.run([
                'gh', 'repo', 'create', repo_name,
                '--description', description,
                visibility,
                '--source', tmpdir,
                '--push'
            ], capture_output=True, text=True, check=True)

            # Get repo URL
            url_result = subprocess.run([
                'gh', 'repo', 'view', '--json', 'url', '-q', '.url'
            ], cwd=tmpdir, capture_output=True, text=True, check=True)

            repo_url = url_result.stdout.strip()

            # Get commit SHA
            sha_result = subprocess.run([
                'git', 'rev-parse', 'HEAD'
            ], cwd=tmpdir, capture_output=True, text=True, check=True)

            commit_sha = sha_result.stdout.strip()

            return {
                "url": repo_url,
                "owner": repo_name.split('/')[0] if '/' in repo_name else None,
                "repo": repo_name.split('/')[1] if '/' in repo_name else repo_name,
                "commit_sha": commit_sha,
                "method": "gh_cli"
            }
```

### Step 2: Add to codeswarm.py Feedback Loop

```python
# In codeswarm.py after Phase 4 feedback collection

# PHASE 5: GitHub Integration
if neo4j and result.get('pattern_id'):
    try:
        push_to_github = input("\nWould you like to push this to GitHub? (y/n): ").strip().lower()

        if push_to_github == 'y':
            # Initialize GitHub client
            github_client = GitHubClient()

            if not github_client.gh_cli_available:
                print("  ⚠️  GitHub CLI not found")
                print("  Install: brew install gh")
                print("  Authenticate: gh auth login")
            else:
                # Ask for repo details
                repo_name = input("  Repository name (e.g., my-website): ").strip()
                if not repo_name:
                    repo_name = f"codeswarm-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

                is_private_input = input("  Make repository private? (y/n, default: n): ").strip().lower()
                is_private = is_private_input == 'y'

                print(f"\n  🚀 Creating GitHub repository: {repo_name}")

                # Get files from implementation output
                files = result.get('implementation', {}).get('parsed_files', {})

                if files:
                    github_result = await github_client.create_and_push_repo(
                        repo_name=repo_name,
                        description=f"Generated by CodeSwarm - {task[:100]}",
                        files=files,
                        is_private=is_private
                    )

                    if github_result:
                        print(f"  ✅ Pushed to GitHub!")
                        print(f"  🔗 {github_result['url']}")

                        # Store in Neo4j
                        await neo4j.link_github_repo(
                            pattern_id=result['pattern_id'],
                            github_url=github_result['url'],
                            commit_sha=github_result['commit_sha']
                        )
                else:
                    print("  ❌ No files to push")

    except (EOFError, KeyboardInterrupt):
        print("\n  Skipping GitHub push")
    except Exception as e:
        print(f"  ⚠️  GitHub push error: {e}")
```

### Step 3: Add Neo4j Methods

```python
# In src/integrations/neo4j_client.py

async def link_github_repo(
    self,
    pattern_id: str,
    github_url: str,
    commit_sha: str
) -> None:
    """
    Link GitHub repository to a code pattern

    Args:
        pattern_id: Pattern ID
        github_url: GitHub repository URL
        commit_sha: Initial commit SHA
    """
    from urllib.parse import urlparse

    # Parse GitHub URL
    # Format: https://github.com/owner/repo
    path_parts = urlparse(github_url).path.strip('/').split('/')
    owner = path_parts[0] if len(path_parts) > 0 else None
    repo = path_parts[1] if len(path_parts) > 1 else None

    cypher = """
    // Find pattern
    MATCH (p:CodePattern {id: $pattern_id})

    // Create or update GitHub repository node
    MERGE (g:GitHubRepository {url: $github_url})
    ON CREATE SET
        g.owner = $owner,
        g.repo = $repo,
        g.created_at = datetime()

    // Update pattern with GitHub info
    SET p.github_url = $github_url,
        p.github_pushed_at = datetime(),
        p.github_repo_name = $owner + '/' + $repo

    // Create relationship
    MERGE (p)-[r:PUSHED_TO_GITHUB]->(g)
    SET r.pushed_at = datetime(),
        r.commit_sha = $commit_sha,
        r.branch = 'main'

    RETURN g.url as url
    """

    async with self.driver.session() as session:
        await session.run(cypher, {
            "pattern_id": pattern_id,
            "github_url": github_url,
            "owner": owner,
            "repo": repo,
            "commit_sha": commit_sha
        })

    logger.info(f"[NEO4J]  Linked GitHub repo: {owner}/{repo}")
```

---

## MCP Server Configuration

If using MCP GitHub Server:

```json
// .claude_code_mcp.json or MCP config
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<token>"
      }
    }
  }
}
```

---

## Security Considerations

1. **Token Storage**: Never store GitHub PAT in code
   - Use environment variables
   - Use GitHub CLI auth (preferred)
   - Use OAuth App flow

2. **Private Repos**: Default to private for user safety
   - Ask explicitly before making public
   - Warn about sensitive data

3. **Commit Attribution**: Always attribute to CodeSwarm
   ```
   🐝 Generated by CodeSwarm

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

4. **File Validation**: Don't push secrets
   - Check for .env files
   - Warn about API keys in code

---

## Testing

```python
# test_github_integration.py

async def test_github_integration():
    """Test GitHub integration"""

    github = GitHubClient()

    # Test 1: Check GitHub CLI available
    assert github.gh_cli_available, "GitHub CLI not installed"

    # Test 2: Create test repo
    files = {
        "index.html": "<html><body>Test</body></html>",
        "README.md": "# Test Repo\n\nGenerated by CodeSwarm"
    }

    result = await github.create_and_push_repo(
        repo_name="codeswarm-test-repo",
        description="Test repository",
        files=files,
        is_private=True
    )

    assert result["url"].startswith("https://github.com/")
    assert result["commit_sha"]

    # Test 3: Link to Neo4j
    neo4j = Neo4jRAGClient()
    await neo4j.link_github_repo(
        pattern_id="test_pattern",
        github_url=result["url"],
        commit_sha=result["commit_sha"]
    )

    print("✅ GitHub integration tests passed")
```

---

## Metrics to Track

1. **Push Rate**: % of generated code pushed to GitHub
2. **Public vs Private**: Distribution of visibility settings
3. **Most Pushed Tasks**: What types of code get pushed most
4. **Time to Push**: Duration from generation to GitHub push
5. **Repo Retention**: Do users keep the repos long-term?

---

## Future Enhancements

1. **Auto-Deploy Actions**: Generate GitHub Actions CI/CD
2. **Pull Request Creation**: Create PR if repo exists
3. **Branch Strategy**: Allow custom branch names
4. **Collaborative Push**: Multiple users push to same org
5. **Template Repos**: Initialize from CodeSwarm templates
6. **Issue Creation**: Auto-create issues for TODOs in code

---

## Implementation Priority

**Phase 5.1 (MVP)** - Week 1:
- [ ] GitHub CLI integration
- [ ] Basic repo creation
- [ ] Neo4j schema extension

**Phase 5.2 (Enhanced)** - Week 2:
- [ ] MCP Server support
- [ ] OAuth flow
- [ ] File validation (secrets detection)

**Phase 5.3 (Advanced)** - Week 3:
- [ ] GitHub Actions generation
- [ ] Pull request creation
- [ ] Analytics dashboard

---

## Success Criteria

- ✅ Users can push to GitHub with 1 command
- ✅ Authentication works via GitHub CLI or MCP
- ✅ All pushes tracked in Neo4j
- ✅ 80%+ success rate for repo creation
- ✅ Average time < 30 seconds from prompt to GitHub URL

---

**Version**: 1.0.0
**Status**: Design Complete - Ready for Implementation
**Dependencies**: GitHub CLI (`gh`) or MCP GitHub Server
**Estimated Effort**: 2-3 days for MVP (Phase 5.1)
