# Quick Start for Blake - CodeSwarm Integration

##  Your Mission
Get 5 API keys + install 2 packages → Test everything → We're demo-ready!

**Time Required**: ~60 minutes total

---

##  FASTEST PATH TO SUCCESS

### Step 1: Install Packages (5 minutes)
```bash
cd /Users/bledden/Documents/codeswarm
pip3 install galileo-observe browser-use workos neo4j
playwright install chromium
```

### Step 2: Get API Keys (50 minutes)
**Follow** [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) **for detailed steps**

Quick checklist:
- [ ] **Galileo** (15 min) → `GALILEO_API_KEY=gal_xxxxx`
- [ ] **Neo4j Aura** (10 min) → `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- [ ] **Browser Use** (already installed above)
- [ ] **WorkOS** (10 min) → `WORKOS_API_KEY`, `WORKOS_CLIENT_ID`
- [ ] **Daytona** (15 min) → `DAYTONA_API_KEY`, `DAYTONA_API_URL`

### Step 3: Update .env (2 minutes)
Edit `/Users/bledden/Documents/codeswarm/.env` and add:

```bash
# Galileo
GALILEO_API_KEY=gal_xxxxx  # From Galileo console
GALILEO_PROJECT=codeswarm-hackathon

# Neo4j Aura
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io  # From credentials file
NEO4J_USER=neo4j
NEO4J_PASSWORD=xxxxx  # From credentials file

# WorkOS
WORKOS_API_KEY=sk_xxxxx  # From WorkOS dashboard
WORKOS_CLIENT_ID=client_xxxxx  # From WorkOS dashboard

# Daytona
DAYTONA_API_KEY=dtna_xxxxx  # From Daytona settings
DAYTONA_API_URL=https://api.daytona.io
DAYTONA_WORKSPACE_ID=  # Leave empty if you didn't create workspace
```

### Step 4: Test Everything (2 minutes)
```bash
python3 test_all_integrations.py
```

**Expected Output**:
```
 ALL SERVICES READY!
You can now run the full CodeSwarm workflow.
```

### Step 5: Paste Credentials to Chat (1 minute)
Copy/paste this into our conversation:

```
GALILEO_API_KEY=gal_xxxxx
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=xxxxx
WORKOS_API_KEY=sk_xxxxx
WORKOS_CLIENT_ID=client_xxxxx
DAYTONA_API_KEY=dtna_xxxxx
DAYTONA_API_URL=https://api.daytona.io
DAYTONA_WORKSPACE_ID=xxxxx (or "none")

Browser Use: Installed 
Playwright: Installed 
Test results: [paste output of test_all_integrations.py]
```

---

##  PRIORITY ORDER

If you're short on time, do them in this order:

1. **Galileo** (15 min) - Most critical for quality evaluation
2. **Neo4j** (10 min) - Needed for RAG storage
3. **Browser Use** (5 min) - Just pip install, no signup
4. **WorkOS** (10 min) - Authentication
5. **Daytona** (15 min) - Deployment (can skip if time-constrained)

---

##  TROUBLESHOOTING

### "No API key found" Error
→ Make sure you copied the key correctly to `.env` file
→ No quotes around the value
→ No spaces before/after the `=`

### Neo4j "Connection refused"
→ Make sure URI starts with `neo4j+s://` (not `bolt://`)
→ Check username is `neo4j`
→ Check password from credentials file

### Browser Use "Not installed"
→ Run: `pip3 install browser-use`
→ Then: `playwright install chromium`

### WorkOS "Invalid credentials"
→ Need BOTH `WORKOS_API_KEY` AND `WORKOS_CLIENT_ID`
→ API key starts with `sk_`
→ Client ID starts with `client_`

---

##  DETAILED GUIDES

- **Full Setup**: [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
- **Integration Status**: [INTEGRATION_READY_STATUS.md](INTEGRATION_READY_STATUS.md)
- **Ready for Integration**: [READY_FOR_INTEGRATION.md](READY_FOR_INTEGRATION.md)

---

##  WHAT'S ALREADY DONE

You don't need to worry about:
-  OpenRouter (already working with your API key)
-  All agent code written
-  LangGraph workflow built
-  Galileo evaluator (real SDK, no mocks)
-  All integration clients written
-  Comprehensive tests created
-  Learning system adapted from Anomaly Hunter

**I just need your API keys to make it all live!**

---

##  AFTER YOU PROVIDE KEYS

I will (estimated 3.5 hours):
1.  Update `.env` file
2.  Run comprehensive tests
3.  Integrate Neo4j RAG into workflow
4.  Integrate Browser Use for documentation scraping
5.  Add WorkOS authentication layer
6.  Add Daytona deployment option
7.  Create full end-to-end demo
8.  Test with your sketch → live website workflow

**Then we're demo-ready!** 

---

##  THE DEMO WILL SHOW

1. You take a photo of a website sketch
2. CodeSwarm:
   - Analyzes with GPT-5-image (Vision)
   - Scrapes docs with Browser Use
   - Retrieves patterns from Neo4j RAG
   - Generates architecture (Claude Sonnet 4.5)
   - Implements code (GPT-5 Pro)
   - Secures it (Claude Opus 4.1)
   - Tests it (Grok-4)
   - Scores with Galileo (90+ threshold)
   - Stores pattern in Neo4j
   - Deploys to Daytona workspace
   - Manages access with WorkOS
3. You have a live website in minutes!

**All 6 sponsors showcased** 

---

## ⏰ TIMELINE

- **Your setup**: 60 minutes
- **My integration**: 3.5 hours
- **Total to demo-ready**: ~4.5 hours

**We have time!** 

---

**Start with Galileo (Section 1 of COMPLETE_SETUP_GUIDE.md) - it's the most critical!**
