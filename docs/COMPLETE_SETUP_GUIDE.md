# Complete Setup Guide - All Services (Blake's Tasks)

##  Overview
This guide walks through setting up ALL required services for CodeSwarm.
**Time Estimate: 45-60 minutes total**

---

## 1⃣ Galileo Observe Setup (15 min)

### Step 1: Create Account
1. Go to: https://www.rungalileo.io/ or https://console.galileo.ai/
2. Click "Sign Up" or "Get Started"
3. Create account with email
4. Verify email

### Step 2: Create Project
1. Log into Galileo Console
2. Click "Create New Project"
3. Project Name: `codeswarm-hackathon`
4. Click "Create"

### Step 3: Get API Key
1. In Galileo Console, go to **Settings** (gear icon)
2. Click **"API Keys"** in left sidebar
3. Click **"Create a new key"**
4. Name: `CodeSwarm Hackathon`
5. Click **"Create"**
6. **COPY the API key** (only shown once!)

### Step 4: Add to .env
```bash
cd /Users/bledden/Documents/codeswarm
# Edit .env file
GALILEO_API_KEY=gal_xxxxxxxxxxxxxxxxxxxxx  # Paste your key here
GALILEO_PROJECT=codeswarm-hackathon
```

### What You Need to Provide Me:
-  `GALILEO_API_KEY` value

---

## 2⃣ Neo4j Aura Setup (10 min)

### Step 1: Create Free Account
1. Go to: https://neo4j.com/cloud/platform/aura-graph-database/
2. Click **"Start Free"**
3. Sign up (no credit card required)
4. Verify email

### Step 2: Create Database Instance
1. Click **"Create Instance"**
2. Choose **"AuraDB Free"** (0.5GB, free forever)
3. Instance Name: `codeswarm-rag`
4. Region: Choose closest to you (US East recommended)
5. Click **"Create"**
6. **IMPORTANT**: Download credentials file
   - File name: `Neo4j-xxxxx-Created-2025-xx-xx.txt`
   - Save this file somewhere safe!

### Step 3: Get Connection Details
Open the downloaded credentials file. It contains:
```
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=xxxxxxxxxxxxxxxxx
```

### Step 4: Add to .env
```bash
# Replace these in .env file:
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io  # From credentials file
NEO4J_USER=neo4j                              # From credentials file
NEO4J_PASSWORD=xxxxxxxxxxxxxxxxx              # From credentials file
```

### What You Need to Provide Me:
-  `NEO4J_URI` (starts with `neo4j+s://`)
-  `NEO4J_USER` (usually `neo4j`)
-  `NEO4J_PASSWORD` (from credentials file)

---

## 3⃣ Browser Use Setup (5 min)

### Step 1: Check Package
Browser Use is a Python package, no API key needed!

### Step 2: Install Package
```bash
cd /Users/bledden/Documents/codeswarm
pip3 install browser-use
```

### Step 3: Verify Installation
```bash
python3 -c "import browser_use; print('Browser Use installed!')"
```

### What You Need to Do:
-  Run: `pip3 install browser-use`
-  Tell me: "Browser Use installed" (or if there's an error)

**Note**: Browser Use uses Playwright under the hood. May need:
```bash
playwright install chromium  # If needed
```

---

## 4⃣ WorkOS Setup (10 min)

### Step 1: Create Account
1. Go to: https://workos.com/
2. Click **"Get Started"** or **"Sign Up"**
3. Create account
4. Verify email

### Step 2: Create Organization
1. Log into WorkOS Dashboard
2. You'll be prompted to create an organization
3. Organization Name: `CodeSwarm`
4. Click **"Create"**

### Step 3: Get API Key
1. In Dashboard, go to **"API Keys"** (left sidebar)
2. Find **"Secret Key"** section
3. **COPY the API Key** (starts with `sk_`)
   - This is shown immediately, keep it safe!

### Step 4: Get Client ID
1. Still in Dashboard, go to **"Configuration"**
2. Find **"Client ID"**
3. **COPY the Client ID** (starts with `client_`)

### Step 5: Add to .env
```bash
WORKOS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxx      # Secret Key
WORKOS_CLIENT_ID=client_xxxxxxxxxxxxxxxxxxxxxx  # Client ID
```

### What You Need to Provide Me:
-  `WORKOS_API_KEY` (starts with `sk_`)
-  `WORKOS_CLIENT_ID` (starts with `client_`)

---

## 5⃣ Daytona Setup (15 min)

### Step 1: Create Account
1. Go to: https://www.daytona.io/
2. Click **"Get Started"** or **"Sign Up"**
3. Create account
4. Verify email

### Step 2: Get API Key
1. Log into Daytona Dashboard
2. Go to **"Settings"** → **"API Keys"**
3. Click **"Generate New API Key"**
4. Name: `CodeSwarm Hackathon`
5. **COPY the API Key**

### Step 3: Get API URL
1. In Dashboard, look for **"API Endpoint"** or **"API URL"**
2. Usually: `https://api.daytona.io` or similar
3. **COPY the API URL**

### Step 4: Create Workspace (Optional)
1. Go to **"Workspaces"**
2. Click **"Create Workspace"**
3. Name: `codeswarm-demo`
4. **COPY the Workspace ID** (if shown)

### Step 5: Add to .env
```bash
DAYTONA_API_KEY=dtna_xxxxxxxxxxxxxxxxx        # API Key
DAYTONA_API_URL=https://api.daytona.io        # API URL
DAYTONA_WORKSPACE_ID=workspace_xxxxx          # Workspace ID (if you created one)
```

### What You Need to Provide Me:
-  `DAYTONA_API_KEY`
-  `DAYTONA_API_URL`
-  `DAYTONA_WORKSPACE_ID` (or tell me you didn't create one)

---

## 6⃣ Verify All Keys (5 min)

### Check .env File
Your `.env` file should now have:

```bash
# OpenRouter (already working)
OPENROUTER_API_KEY=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

# Galileo
GALILEO_API_KEY=gal_xxxxxxxxxxxxxxxxxxxxx
GALILEO_PROJECT=codeswarm-hackathon

# Neo4j
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=xxxxxxxxxxxxxxxxx

# Browser Use (no key needed, just install package)

# WorkOS
WORKOS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxx
WORKOS_CLIENT_ID=client_xxxxxxxxxxxxxxxxxxxxxx

# Daytona
DAYTONA_API_KEY=dtna_xxxxxxxxxxxxxxxxx
DAYTONA_API_URL=https://api.daytona.io
DAYTONA_WORKSPACE_ID=workspace_xxxxx
```

---

##  BLAKE'S CHECKLIST

### Services to Set Up:
- [ ] Galileo Observe (15 min)
  - [ ] Create account
  - [ ] Create project "codeswarm-hackathon"
  - [ ] Get API key
  - [ ] Add `GALILEO_API_KEY` to .env

- [ ] Neo4j Aura (10 min)
  - [ ] Create free account
  - [ ] Create instance "codeswarm-rag"
  - [ ] Download credentials file
  - [ ] Add `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` to .env

- [ ] Browser Use (5 min)
  - [ ] Run: `pip3 install browser-use`
  - [ ] Confirm installed

- [ ] WorkOS (10 min)
  - [ ] Create account
  - [ ] Get API key (starts with `sk_`)
  - [ ] Get Client ID (starts with `client_`)
  - [ ] Add `WORKOS_API_KEY` and `WORKOS_CLIENT_ID` to .env

- [ ] Daytona (15 min)
  - [ ] Create account
  - [ ] Get API key
  - [ ] Get API URL
  - [ ] (Optional) Create workspace and get ID
  - [ ] Add `DAYTONA_API_KEY`, `DAYTONA_API_URL`, `DAYTONA_WORKSPACE_ID` to .env

### Final Step:
- [ ] Send Claude the updated values for .env file

---

##  COMMON ISSUES

### Issue: Can't find API key in dashboard
**Solution**: Look for "Settings" → "API Keys" or "Developers" section

### Issue: Neo4j connection refused
**Solution**: Make sure using `neo4j+s://` (with +s) not `bolt://`

### Issue: Browser Use import error
**Solution**: Run `playwright install chromium`

### Issue: WorkOS authentication fails
**Solution**: Double-check both API key AND Client ID are correct

### Issue: Daytona workspace not found
**Solution**: Workspace ID is optional, can be empty string `""`

---

## ⏰ TIMELINE

| Service | Time | Status |
|---------|------|--------|
| Galileo | 15 min | ⏳ |
| Neo4j | 10 min | ⏳ |
| Browser Use | 5 min | ⏳ |
| WorkOS | 10 min | ⏳ |
| Daytona | 15 min | ⏳ |
| **Total** | **55 min** | ⏳ |

---

##  WHAT TO SEND CLAUDE

Once you're done, send me:

```
GALILEO_API_KEY=gal_xxxxx
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=xxxxx
WORKOS_API_KEY=sk_xxxxx
WORKOS_CLIENT_ID=client_xxxxx
DAYTONA_API_KEY=dtna_xxxxx
DAYTONA_API_URL=https://api.daytona.io
DAYTONA_WORKSPACE_ID=workspace_xxxxx (or empty if none)
```

And confirm: "Browser Use pip installed"

Then I'll integrate everything and we'll test live!

---

**Start with Galileo first (most critical), then do the others!** 
