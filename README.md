# 🐝 CodeSwarm

**Self-Improving Multi-Agent AI Coding System**

CodeSwarm orchestrates 5 specialized AI models to generate production-quality code with real-time quality evaluation, autonomous learning, and complete observability.

---

## 🎯 What is CodeSwarm?

CodeSwarm demonstrates how multiple AI agents can collaborate to generate high-quality code:

- **5 Specialized Agents**: Architecture, Implementation, Security, Testing, and Vision
- **Real-Time Quality Scoring**: Galileo Observe evaluates each output with a 90+ threshold
- **Self-Improving**: Stores successful patterns in Neo4j for future retrieval
- **Production-Ready**: Authentication, deployment, and observability built-in

### Key Features

✅ **Multi-Model Orchestration** - Uses the best AI model for each task  
✅ **Quality Enforcement** - 90+ score threshold with iterative improvement  
✅ **RAG-Powered** - Retrieves proven patterns before generation  
✅ **Safe Parallel Execution** - Concurrent agents without conflicts  
✅ **Full Integration** - 6 sponsor services working together  
✅ **Autonomous Learning** - Improves from successful outcomes  
✅ **Interactive CLI** - Easy-to-use command-line interface

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (3.11+ for Browser Use)
- Git
- API keys (see Setup below)

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/bledden/codeswarm.git
cd codeswarm

# Install dependencies
pip3 install -r requirements.txt

# Copy environment template and add your API keys
cp .env.example .env
nano .env
\`\`\`

### Get API Keys

You'll need API keys from these services:

1. **OpenRouter** (Required) - https://openrouter.ai/keys
2. **Galileo Observe** (Required) - https://app.galileo.ai
3. **Neo4j Aura** (Required) - https://neo4j.com/cloud/aura/
4. **WorkOS** (Required) - https://dashboard.workos.com
5. **Daytona** (Required) - https://app.daytona.io
6. **Tavily** (Optional) - https://tavily.com
7. **W&B Weave** (Optional) - https://wandb.ai

> See \`.env.example\` for all required environment variables  
> 📖 **Detailed setup**: [SETUP_GUIDE.md](SETUP_GUIDE.md)

### Verify Installation

\`\`\`bash
python3 test_services_quick.py
\`\`\`

Expected:
\`\`\`
✅ OpenRouter: Working
✅ Neo4j: Connected
✅ Galileo: Working
✅ WorkOS: Connected
✅ Daytona: Connected
\`\`\`

---

## 📖 Usage

### CLI (Recommended)

The easiest way to use CodeSwarm is through the CLI:

\`\`\`bash
# Generate code from a task description
./codeswarm generate "Create a REST API for user authentication"

# Generate from a sketch/image
./codeswarm generate "Build a todo app" --image sketch.png

# View configuration and stats
./codeswarm status

# View generation history
./codeswarm history

# Configure settings
./codeswarm configure
\`\`\`

#### CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `generate <task>` | Generate code from task | `./codeswarm generate "Create a chat app"` |
| `generate <task> --image <path>` | Generate from image | `./codeswarm generate "Build UI" -i sketch.png` |
| `generate <task> --deploy` | Generate and deploy to Daytona | `./codeswarm generate "API" --deploy` |
| `generate <task> --no-scrape` | Skip documentation scraping | `./codeswarm generate "task" --no-scrape` |
| `status` | Show config and stats | `./codeswarm status` |
| `history` | Show past generations | `./codeswarm history --limit 20` |
| `configure` | Interactive configuration | `./codeswarm configure` |

#### Example Session

\`\`\`bash
$ ./codeswarm generate "Create a secure REST API for managing tasks"

🐝 CODESWARM - Multi-Agent AI Coding System
================================================================================

📝 Task: Create a secure REST API for managing tasks

⚙️  Initializing services...
  ✅ OpenRouter connected
  ✅ Neo4j connected
  ✅ Galileo initialized
  ✅ WorkOS initialized
  ✅ Daytona connected

🎯 5/6 services active

────────────────────────────────────────────────────────────────────────────────
  GENERATING CODE
────────────────────────────────────────────────────────────────────────────────

[1/8] 🔐 Authenticating user with WorkOS...
      ✅ User cli-user authenticated

[2/8] 🗄️  Retrieving similar patterns from Neo4j...
      ✅ Retrieved 2 patterns (90+ quality)

[3/8] 🌐 Scraping documentation with Tavily...
      ✅ Scraped 3 docs

[5/8] 🏗️  Architecture Agent (Claude Sonnet 4.5)...
      ✅ Score: 94.0/100
      ✅ Output: 2,340 chars

[6/8] 💻 Implementation & Security (Parallel)...
      ✅ Implementation: 96.0/100 (18,450 chars)
      ✅ Security: 98.0/100 (12,890 chars)

[7/8] 🧪 Testing Agent (Grok-4)...
      ✅ Score: 92.0/100

📊 Average Quality Score: 95.0/100
💾 Storing pattern in Neo4j (quality: 95.0 >= 90.0)...
✅ Pattern stored: pattern_20251018_220000

────────────────────────────────────────────────────────────────────────────────
  📊 RESULTS
────────────────────────────────────────────────────────────────────────────────

Quality Scores:
  Architecture:    94.0/100
  Implementation:  96.0/100
  Security:        98.0/100
  Testing:         92.0/100
  ────────────────────────────────
  Average:         95.0/100

Quality Threshold: ✅ MET (90.0+)

📦 Pattern stored in Neo4j: pattern_20251018_220000
🔍 Used 2 similar patterns from RAG

💾 Results saved to: output/generation_20251018_220000.json
📁 Code files saved to: output/code_20251018_220000
\`\`\`

### Python API

For programmatic access:

\`\`\`python
from integrations import OpenRouterClient, Neo4jRAGClient
from evaluation import GalileoEvaluator
from orchestration import FullCodeSwarmWorkflow

async def generate_code():
    async with OpenRouterClient() as openrouter:
        async with Neo4jRAGClient() as neo4j:
            galileo = GalileoEvaluator()

            workflow = FullCodeSwarmWorkflow(
                openrouter_client=openrouter,
                neo4j_client=neo4j,
                galileo_evaluator=galileo
            )

            result = await workflow.execute(
                task="Create a REST API for user authentication"
            )

            print(f"Score: {result['avg_score']:.1f}/100")
\`\`\`

### Demo Scripts

\`\`\`bash
# Full integration demo (all 6 services)
python3 demo_full_integration.py

# Quick service verification
python3 test_services_quick.py
\`\`\`

---

## 🏗️ Architecture

### Workflow

1. **RAG Retrieval** (Neo4j) → Get similar 90+ patterns
2. **Doc Scraping** (Tavily) → Find relevant documentation
3. **Architecture** (Claude) → Design system structure
4. **Parallel Execution**:
   - Implementation (GPT-5) → Generate code
   - Security (Claude) → Add security measures
5. **Testing** (Grok-4) → Create tests
6. **Quality Check** (Galileo) → Score outputs (90+)
7. **Pattern Storage** (Neo4j) → Save if successful
8. **Deployment** (Daytona) → Optional deployment

### Models

| Agent | Model | Specialty |
|-------|-------|-----------|
| Architecture | Claude Sonnet 4.5 | System design |
| Implementation | GPT-5 Pro | Production code |
| Security | Claude Opus 4.1 | Security practices |
| Testing | Grok-4 | Test generation |
| Vision | GPT-5 Image | Image analysis |

---

## 📊 Project Structure

\`\`\`
codeswarm/
├── codeswarm                # CLI wrapper script
├── codeswarm_cli.py        # CLI implementation
├── src/
│   ├── agents/              # 5 specialized AI agents
│   ├── integrations/        # Service clients
│   ├── orchestration/       # Workflow coordination
│   ├── evaluation/          # Quality assessment
│   └── learning/            # Autonomous improvement
├── tests/                   # Test suite
├── output/                  # CLI output directory
├── cache/                   # CLI cache and history
├── demo_full_integration.py # Full demo
├── .env.example             # Environment template
└── README.md                # This file
\`\`\`

---

## 🧪 Testing

\`\`\`bash
# Quick service test
python3 test_services_quick.py

# Full integration test
python3 demo_full_integration.py
\`\`\`

---

## 🔧 Configuration

### Via CLI

\`\`\`bash
./codeswarm configure
\`\`\`

Interactive prompts will let you adjust:
- Quality threshold (default: 90)
- Max iterations (default: 3)
- Auto deployment (default: false)
- Documentation scraping (default: true)

### Via Environment

All configuration via \`.env\` file. Required variables:

\`\`\`bash
OPENROUTER_API_KEY=your_key_here
GALILEO_API_KEY=your_key_here
GALILEO_CONSOLE_URL=https://app.galileo.ai
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
WORKOS_API_KEY=your_key_here
WORKOS_CLIENT_ID=your_client_id_here
DAYTONA_API_KEY=your_key_here
DAYTONA_API_URL=https://app.daytona.io/api
\`\`\`

---

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions
- **[FULL_SYSTEM_DOCUMENTATION.md](FULL_SYSTEM_DOCUMENTATION.md)** - Complete technical documentation (internal)
- **[READY_FOR_HACKATHON.md](READY_FOR_HACKATHON.md)** - Presentation guide (internal)

---

## 🤝 Contributing

Contributions welcome!

1. Fork the repository
2. Create feature branch (\`git checkout -b feature/AmazingFeature\`)
3. Commit changes (\`git commit -m 'Add AmazingFeature'\`)
4. Push to branch (\`git push origin feature/AmazingFeature\`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Sponsors

- [Anthropic](https://www.anthropic.com/) - Claude AI models
- [Galileo](https://www.galileo.ai/) - Quality evaluation
- [Neo4j](https://neo4j.com/) - Graph database
- [WorkOS](https://workos.com/) - Authentication
- [Daytona](https://daytona.io/) - Development workspaces
- [Browser Use](https://browseruse.com/) - Web automation
- [Weights & Biases](https://wandb.ai/) - Observability

---

## 💡 Tips

**CLI Usage**:
- Use \`./codeswarm status\` to check your current configuration
- View \`./codeswarm history\` to see past generations and scores
- Generated code is saved to \`output/code_<timestamp>/\` directory

**Performance**:
- Complex tasks may take 2-3 minutes
- Use RAG patterns for faster similar tasks
- Lower threshold for speed (but less quality)

**Quality**:
- Default 90+ threshold ensures production quality
- Agents iterate up to 3 times to meet threshold
- Check Galileo dashboard for detailed metrics

---

**Built for hackathon • ⭐ Star if helpful!**
