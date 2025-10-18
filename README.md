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

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (3.11+ for Browser Use)
- Git
- API keys (see Setup below)

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/yourusername/codeswarm.git
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

> See `.env.example` for all required environment variables

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

### Basic Example

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

### Run Full Demo

\`\`\`bash
python3 demo_full_integration.py
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
├── src/
│   ├── agents/              # 5 specialized AI agents
│   ├── integrations/        # Service clients
│   ├── orchestration/       # Workflow coordination
│   ├── evaluation/          # Quality assessment
│   └── learning/            # Autonomous improvement
├── tests/                   # Test suite
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

All configuration via `.env` file. Required variables:

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

## 🙏 Sponsors

- [Anthropic](https://www.anthropic.com/) - Claude AI models
- [Galileo](https://www.galileo.ai/) - Quality evaluation
- [Neo4j](https://neo4j.com/) - Graph database
- [WorkOS](https://workos.com/) - Authentication
- [Daytona](https://daytona.io/) - Development workspaces
- [Browser Use](https://browseruse.com/) - Web automation
- [Weights & Biases](https://wandb.ai/) - Observability

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

**Built for hackathon • ⭐ Star if helpful!**
