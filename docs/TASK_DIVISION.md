# Task Division - Blake & Claude

##  API KEYS NEEDED (Blake's Tasks)

### Critical for Demo
- [ ] **ANTHROPIC_API_KEY** - Currently: `your_anthropic_key_here`
  - Need for: Claude Sonnet 4.5 (Architecture) & Claude Opus 4.1 (Security)
  - Where to get: https://console.anthropic.com/
  - Priority: **P0 - CRITICAL**

- [ ] **GALILEO_API_KEY** - Currently: `your_galileo_key_here`
  - Need for: Real quality scoring (currently using mock)
  - Where to get: Galileo Observe dashboard
  - Priority: **P1 - HIGH** (mock works but real is better)

### Optional for Demo
- [ ] **WORKOS_API_KEY** - Currently: `your_workos_key_here`
  - Need for: Team authentication
  - Priority: **P3 - LOW** (can show as roadmap feature)

- [ ] **WORKOS_CLIENT_ID** - Currently: `your_workos_client_id_here`
  - Need for: WorkOS integration
  - Priority: **P3 - LOW**

### Already Have (Working)
-  **OPENROUTER_API_KEY** - Working! (All tests passed)
-  **OPENAI_API_KEY** - Working!
-  **WANDB_API_KEY** - Working! (for Weave observability)

---

## 🟢 BLAKE'S TASK LIST (While Claude Works)

### Priority 1: Get API Keys (10-15 min)
1. [ ] **Get Anthropic API Key**
   - Go to https://console.anthropic.com/
   - Create account or login
   - Get API key
   - Replace `your_anthropic_key_here` in `.env`
   - This enables Claude Sonnet 4.5 & Opus 4.1

2. [ ] **Get Galileo API Key** (if possible)
   - Check Galileo Observe dashboard
   - Get API key
   - Replace `your_galileo_key_here` in `.env`
   - Or: Skip this, mock works fine for demo

### Priority 2: Create Sample Sketch (10-15 min)
3. [ ] **Create a sketch image** (optional but cool for demo)
   - Option A: Go to https://excalidraw.com
   - Draw simple landing page wireframe:
     - Header with logo + nav
     - Hero section with CTA buttons
     - 3 feature cards
     - Pricing section
     - Contact form
   - Export as PNG
   - Save to: `/Users/bledden/Documents/codeswarm/demo/sketch.jpg`

   - Option B: Use the text wireframe we created
     - Located at: `demo/wireframe.txt`
     - No image needed, demo works without it

### Priority 3: Review Generated Code (5 min)
4. [ ] **Check the demo output**
   - Open: `/Users/bledden/Documents/codeswarm/demo_output/quick_demo_20251018_134131.txt`
   - Review: Is the generated code actually good?
   - Check: Architecture makes sense?
   - Check: Implementation is complete?

5. [ ] **Test the generated code** (optional)
   - Try running the generated Node.js code
   - See if it actually works
   - Report any issues

### Priority 4: Prepare for Demo (10-15 min)
6. [ ] **Read the demo script**
   - Open: `DEMO_GUIDE.md`
   - Read through the 1:45 min script
   - Practice explaining each section
   - Time yourself

7. [ ] **Prepare backup plan**
   - Screenshot some good results
   - Have explanation ready if APIs fail
   - Know what to say about optional features

### Priority 5: Recording (15-20 min - if time)
8. [ ] **Record demo video** (optional)
   - Set up screen recording
   - Run: `python3 demo.py`
   - Narrate while it runs
   - Save as MP4
   - Upload to YouTube (unlisted)

---

##  CLAUDE'S TASK LIST (Automated Work)

### Currently Running
-  Tests completed successfully (all PASSED)
-  Demo ran successfully (92/100 scores)

### Next Tasks (Automated)
1. [x]  Complete demo_quick.py test - DONE (92/100)
2. [ ] Run full 4-agent demo with real APIs
3. [ ] Test quality improvement loop (force score < 90)
4. [ ] Review actual generated code quality
5. [ ] Polish terminal output (add colors/progress bars)
6. [ ] Test error handling (API failures)
7. [ ] Create final submission checklist

### Once Blake Adds Anthropic Key
8. [ ] Test Claude Sonnet 4.5 (Architecture Agent)
9. [ ] Test Claude Opus 4.1 (Security Agent)
10. [ ] Run full 4-agent workflow with all real models
11. [ ] Compare quality with/without real Claude models

### Once Blake Adds Galileo Key (Optional)
12. [ ] Switch from mock to real Galileo SDK
13. [ ] Test real quality scoring
14. [ ] Verify 90+ threshold logic

---

## ⏱ TIME ESTIMATES

### Blake's Critical Path (30-40 min)
- Get Anthropic key: 10 min
- Get Galileo key OR skip: 5 min
- Review demo guide: 10 min
- Create/find sketch image: 15 min
- **Total: 40 minutes**

### Claude's Critical Path (30-40 min)
- Full 4-agent demo: 15 min (running)
- Test with real Anthropic models: 10 min
- Polish output: 10 min
- Final validation: 5 min
- **Total: 40 minutes**

### Parallel Execution
- Both can work simultaneously
- **Total real time: 40 minutes to demo-ready**

---

##  SUCCESS CRITERIA

### Minimum for Demo (Must Have)
- [x]  OpenRouter working (DONE)
- [ ] ⏳ Anthropic API key added
- [ ] ⏳ Full 4-agent demo runs successfully
- [ ] ⏳ Generated code is good quality
- [x]  Demo script prepared (DONE)

### Nice to Have
- [ ] Real Galileo scoring (vs mock)
- [ ] Actual sketch image (vs wireframe)
- [ ] Demo video recorded
- [ ] All sponsor integrations working

### Optional
- [ ] WorkOS integration
- [ ] Neo4j RAG deployed
- [ ] Browser Use integration

---

##  COMMUNICATION

### Blake Should Report When:
-  Anthropic API key added to `.env`
-  Galileo API key added (or confirmed skipping)
-  Sketch image ready (or confirmed using wireframe)
-  Any issues with generated code quality
-  Any API errors

### Claude Will Report When:
-  Each test completes
-  Full demo runs successfully
-  Code quality validated
-  Any bugs found
-  Any blockers

---

##  CURRENT STATUS

### What's Working Now
-  OpenRouter client (real API calls)
-  Individual agents (Architecture, Implementation tested)
-  Parallel execution (269s = 4.5 min)
-  Sequential flow (Architecture → Implementation)
-  Mock Galileo scoring (realistic)
-  Demo script written
-  Documentation complete

### What Needs Blake's Input
- ⏳ Anthropic API key (for Claude models)
- ⏳ Galileo API key (optional, mock works)
- ⏳ Sketch image (optional, wireframe works)

### What Needs Testing
- ⏳ Full 4-agent workflow end-to-end
- ⏳ Quality improvement loop (< 90 score)
- ⏳ Vision agent with real image
- ⏳ Error handling (API failures)

---

##  DEMO READINESS

**Current**: 75% ready
**With Anthropic key**: 90% ready
**With sketch + Galileo**: 95% ready

**Blocker**: Need Anthropic API key to use Claude models
**Workaround**: Can use GPT-5 for all agents if needed

---

##  QUESTIONS FOR BLAKE

1. **Do you have Anthropic API access?**
   - If yes: Please add key to `.env`
   - If no: We can use GPT-5 for all agents instead

2. **Do you have Galileo API access?**
   - If yes: Please add key to `.env`
   - If no: Mock works fine for demo

3. **Do you want to create a sketch image?**
   - If yes: Use Excalidraw or draw on paper
   - If no: We have a text wireframe that works

4. **Time remaining for hackathon?**
   - Need to know for prioritization
   - Can we skip optional features?

---

**Next: Waiting for Blake to add Anthropic API key, then I'll run full demo with real Claude models** 
