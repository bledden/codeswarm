# CodeSwarm Setup Guide

Complete step-by-step instructions for setting up CodeSwarm.

---

## Prerequisites

- Python 3.9 or higher
- Git
- Internet connection
- Email address for service signups

---

## Step 1: Clone and Install

\`\`\`bash
# Clone repository
git clone https://github.com/yourusername/codeswarm.git
cd codeswarm

# Install Python dependencies
pip3 install -r requirements.txt

# Copy environment template
cp .env.example .env
\`\`\`

---

## Step 2: Get API Keys

### 1. OpenRouter (Required - 5 minutes)

**Purpose**: Multi-model LLM gateway for all AI models

1. Go to https://openrouter.ai
2. Click "Sign Up" (can use Google/GitHub)
3. Navigate to "Keys" in sidebar
4. Click "Create Key"
5. Copy the key (starts with `sk-or-v1-`)
6. Add to `.env`:
   \`\`\`
   OPENROUTER_API_KEY=your_key_here
   \`\`\`

---

### 2. Galileo Observe (Required - 15 minutes)

**Purpose**: Real-time quality evaluation and scoring

1. Go to https://app.galileo.ai
2. Sign up with email or Google
3. Create a new project:
   - Click "New Project"
   - Name: "codeswarm-hackathon"
   - Type: "Observe"
4. Go to Settings → API Keys
5. Click "Generate API Key"
6. Copy the key
7. Add to `.env`:
   \`\`\`
   GALILEO_API_KEY=your_key_here
   GALILEO_PROJECT=codeswarm-hackathon
   GALILEO_CONSOLE_URL=https://app.galileo.ai
   \`\`\`

---

### 3. Neo4j Aura (Required - 10 minutes)

**Purpose**: Graph database for RAG pattern storage

1. Go to https://neo4j.com/cloud/aura/
2. Sign up (free tier available)
3. Click "Create Instance"
   - Instance name: "codeswarm-rag"
   - Region: Choose closest to you
   - Size: Free tier is sufficient
4. Wait for instance to be ready (~2 minutes)
5. Click "Download Credentials" - save this file!
6. Open the credentials file and find:
   - URI (starts with `neo4j+s://`)
   - Username (usually `neo4j`)
   - Password
7. Add to `.env`:
   \`\`\`
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password_from_file
   \`\`\`

---

### 4. WorkOS (Required - 10 minutes)

**Purpose**: Team authentication and SSO

1. Go to https://dashboard.workos.com
2. Sign up with email
3. Create an application:
   - Name: "CodeSwarm"
   - Type: "Web Application"
4. Go to API Keys section
5. Copy:
   - API Key (starts with `sk_test_`)
   - Client ID (starts with `client_`)
6. Add to `.env`:
   \`\`\`
   WORKOS_API_KEY=your_api_key_here
   WORKOS_CLIENT_ID=your_client_id_here
   \`\`\`

---

### 5. Daytona (Required - 15 minutes)

**Purpose**: Development workspace and deployment

1. Go to https://app.daytona.io
2. Sign up with email or GitHub
3. Go to Settings → API Keys
4. Click "Generate API Key"
5. Copy the key
6. Add to `.env`:
   \`\`\`
   DAYTONA_API_KEY=your_key_here
   DAYTONA_API_URL=https://app.daytona.io/api
   \`\`\`

---

### 6. Tavily (Optional - 5 minutes)

**Purpose**: Documentation scraping (alternative to Browser Use)

1. Go to https://tavily.com
2. Sign up with email
3. Navigate to API Keys
4. Copy your key
5. Add to `.env`:
   \`\`\`
   TAVILY_API_KEY=your_key_here
   \`\`\`

---

### 7. W&B Weave (Optional - 5 minutes)

**Purpose**: Observability and tracking

1. Go to https://wandb.ai
2. Sign up with email or GitHub
3. Go to Settings → API Keys
4. Copy your key
5. Add to `.env`:
   \`\`\`
   WANDB_API_KEY=your_key_here
   WANDB_PROJECT=codeswarm-hackathon
   \`\`\`

---

## Step 3: Verify Setup

\`\`\`bash
# Test all service connections
python3 test_services_quick.py
\`\`\`

**Expected output**:
\`\`\`
✅ OpenRouter: Working
✅ Neo4j: Connected (X patterns stored)
✅ Galileo: Working (test score: XX/100)
✅ WorkOS: Connected
✅ Daytona: Connected
\`\`\`

**If any service fails**:
- Check the API key is correctly copied to `.env`
- Ensure no extra spaces before/after the `=`
- Verify the service is accessible from your network
- Check the service dashboard for any issues

---

## Step 4: Run Demo

\`\`\`bash
# Run full integration demo
python3 demo_full_integration.py
\`\`\`

This will execute the complete workflow and save results to `demo_output/`.

---

## Troubleshooting

### "Module not found" errors

\`\`\`bash
pip3 install -r requirements.txt
\`\`\`

### Galileo connection fails

- Verify `GALILEO_CONSOLE_URL=https://app.galileo.ai`
- Check your project name matches in Galileo dashboard
- Ensure API key is active

### Neo4j connection refused

- Ensure URI starts with `neo4j+s://` (not `bolt://`)
- Check username is `neo4j`
- Verify password from credentials file

### OpenRouter timeout

- Complex tasks may take 2-3 minutes
- Check your internet connection
- Verify API key is valid

---

## Next Steps

1. ✅ Read [README.md](README.md) for usage examples
2. ✅ Check [FULL_SYSTEM_DOCUMENTATION.md](FULL_SYSTEM_DOCUMENTATION.md) for technical details
3. ✅ Review [READY_FOR_HACKATHON.md](READY_FOR_HACKATHON.md) for presentation guide

---

## Security Notes

- ⚠️ Never commit `.env` file to Git
- ⚠️ Keep API keys private
- ⚠️ Rotate keys if accidentally exposed
- ⚠️ Use test/development keys for hackathons

---

**Need help?** Check the documentation or file an issue on GitHub.
