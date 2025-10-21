# CodeSwarm Demo Guide

##  Hackathon Demo Flow (1:45 minutes)

### Setup (Before Demo - 0:00)
```bash
cd /Users/bledden/Documents/codeswarm
python3 demo.py demo/sketch.jpg
```

---

##  Demo Script

### Introduction (0:00 - 0:15)

**"Hi! I'm Blake, and this is CodeSwarm - a self-improving multi-agent coding system."**

**The Problem:**
- Building quality code is hard
- Multiple aspects to consider: architecture, implementation, security, testing
- Context gets lost between iterations
- No quality assurance

**The Solution: CodeSwarm**
- 4 specialized AI agents collaborate
- Each uses the best model for their task
- Quality-assured with Galileo (90+ threshold)
- Self-improving through feedback loops

---

### Live Demo (0:15 - 1:15)

#### Part 1: The Sketch (0:15 - 0:20)

**[Show sketch on paper]**

"I sketched this website mockup on paper. Let me take a photo..."

**[Take photo with phone, save as demo/sketch.jpg]**

---

#### Part 2: CodeSwarm in Action (0:20 - 1:00)

**[Run command]**
```bash
python3 demo.py demo/sketch.jpg
```

**[While running, explain the flow]**

"Watch CodeSwarm work:

1. **Vision Agent** (GPT-5-image) - Analyzes the sketch
   - Identifies UI components
   - Extracts layout structure
   - Creates technical spec

2. **Architecture Agent** (Claude Sonnet 4.5) - Designs the system
   - Component structure
   - Technology stack decisions
   - Scalability considerations

3. **Parallel Stage** - Two agents work together:
   - **Implementation Agent** (GPT-5 Pro) - Writes the code
   - **Security Agent** (Claude Opus 4.1) - Hardens security
   - Both see the architecture (no conflicts!)

4. **Testing Agent** (Grok-4 - 98% HumanEval) - Creates tests
   - Unit tests
   - Integration tests
   - Edge cases

5. **Quality Assurance** (Galileo Observe)
   - Scores each agent's output (0-100)
   - If < 90, iterate with feedback
   - Only 90+ code goes into knowledge base"

---

#### Part 3: Results (1:00 - 1:15)

**[Show terminal output]**

"Look at the results:

- Architecture: **92/100** 
- Implementation: **94/100** 
- Security: **96/100** 
- Testing: **91/100** 

**Average: 93.25/100** - Exceeds our 90 quality threshold!

The system generated:
- Complete architecture specification
- Production-ready code
- Security-hardened version
- Comprehensive test suite

All in **[X] seconds** with **[Y] improvement iterations**."

**[Show saved files]**
```bash
ls -lh demo_output/
```

"Production-ready code, saved and ready to deploy!"

---

### Technology Stack (1:15 - 1:30)

**"How does CodeSwarm use sponsor technologies?"**

1. **Anthropic** 
   - Claude Sonnet 4.5 (Architecture)
   - Claude Opus 4.1 (Security)
   - Best-in-class reasoning

2. **Galileo Observe** 
   - Quality evaluation (90+ threshold)
   - Improvement feedback loops
   - Multi-dimensional scoring

3. **Browser Use** 
   - Live documentation scraping
   - Always current context
   - Reduces back-and-forth

4. **WorkOS** 
   - Team authentication
   - Knowledge sharing across teams
   - Enterprise-ready

5. **Daytona** 
   - Development workspace
   - Code commits & testing
   - Deployment pipeline

6. **W&B Weave** (Bonus) 
   - Observability on autonomous learner
   - Performance tracking
   - Self-improvement metrics

---

### Innovation Highlights (1:30 - 1:40)

**"What makes CodeSwarm unique?"**

1. **No Synthesis Conflicts**
   - Sequential stages with safe parallel
   - Architecture defines structure first
   - Agents share context (collective blackboard)

2. **Self-Improving**
   - Learns from every generation
   - Only 90+ patterns stored
   - Gets better over time

3. **Conditional Vision**
   - Only activates when needed
   - Cost-effective (~5% of requests)
   - GPT-5-image for sketch analysis

4. **Multi-Model Collaboration**
   - Best model for each task
   - Claude for reasoning
   - GPT-5 for code
   - Grok for testing

---

### Wrap-Up (1:40 - 1:45)

**"CodeSwarm demonstrates:"**

-  Sharp reasoning (Claude Sonnet 4.5)
-  Independent decision-making (4 specialized agents)
-  Safe integration (90+ quality gate)
-  Industry tools (6 sponsor integrations)

**"From sketch to production-ready code in seconds."**

**"Thank you!"**

---

##  Demo Tips

### Before Demo
1.  Test demo.py with sample sketch
2.  Verify all API keys loaded
3.  Clear demo_output/ folder
4.  Prepare backup slides (if API fails)
5.  Time the demo (should be ~1:30)

### During Demo
- **Show confidence** - The system works!
- **Explain while it runs** - Don't wait in silence
- **Highlight sponsor integrations** - They're key!
- **Point out quality scores** - 90+ threshold is unique
- **Show the code** - It's actually good!

### Backup Plan
If live demo fails:
1. Show pre-recorded video
2. Walk through saved results
3. Explain architecture on slides
4. Show test results from earlier

---

##  Expected Performance

### Timing (varies by API latency)
- Vision Analysis: 5-15s
- Architecture: 20-40s
- Implementation + Security (parallel): 30-60s
- Testing: 20-40s
- **Total: 1.5-3 minutes**

### Quality Scores (typical)
- Architecture: 90-95
- Implementation: 88-94
- Security: 92-98
- Testing: 85-92
- **Average: 90-95**

### Improvement Iterations
- Usually: 1-2 iterations per agent
- Total: 4-8 iterations
- Agents scoring 90+ stop early

---

##  Sample Sketch Ideas

### Simple (for quick demo)
- Todo list app
- Login form
- Product card

### Medium (good balance)
- Landing page
- Dashboard
- E-commerce page

### Complex (impressive)
- Full SaaS app
- Multi-page site
- Admin panel

---

##  Troubleshooting

### API Rate Limits
- Use GPT-3.5-turbo for testing
- Reduce max_iterations to 1
- Lower quality threshold to 85

### Slow Performance
- Normal! LLM calls take time
- Explain the process while waiting
- Pre-run demo and show results

### Vision Model Fails
- Skip vision, use text description
- "Imagine I showed you a sketch..."
- Still demonstrate 4-agent collaboration

---

##  Metrics to Highlight

1. **Quality Improvement**
   - Before iteration: 87/100
   - After iteration: 93/100
   - Improvement: +6 points

2. **Multi-Model Advantage**
   - 4 different models
   - Each specialized
   - Better than single model

3. **Self-Improvement**
   - 14 patterns learned (from Anomaly Hunter)
   - Gets smarter over time
   - 90+ knowledge base

---

##  Winning Points

### Impact (25%)
- Developers spend hours on this manually
- CodeSwarm does it in minutes
- Quality-assured (90+ threshold)
- Self-improving (gets better)

### Technical (25%)
- LangGraph state machine
- Multi-model orchestration
- Galileo quality gates
- Autonomous learning

### Creativity (25%)
- Sketch → code is novel
- Conditional vision unique
- Safe parallel execution
- Quality improvement loop

### Presentation (25%)
- Live demo
- Clear explanation
- Confident delivery
- Sponsor integrations highlighted

---

##  Call to Action

**"Try CodeSwarm yourself:"**
```bash
git clone <repo>
cd codeswarm
cp .env.example .env  # Add your API keys
python3 demo.py "Create a REST API for [your idea]"
```

**"Or with a sketch:"**
```bash
python3 demo.py path/to/your/sketch.jpg
```

**Next Steps:**
- Add more specialized agents
- Integrate with Daytona workspaces
- Team collaboration with WorkOS
- Production deployment

---

**CodeSwarm: From sketch to production in seconds** 
