# Which Demo Should I Use?

CodeSwarm has different demos for different purposes. Here's how to choose:

---

## Quick Decision Tree

```
Do you need to VALIDATE the code generated?
│
├─ YES → Use demo_real.py (generates actual code)
│
└─ NO  → Do you need to present to an audience?
         │
         ├─ YES → Use demo_presentation.py (fast, pretty)
         │
         └─ NO  → Use demo.py (full workflow with vision)
```

---

## 1. `demo_presentation.py` - For Presentations

**Purpose:** Show the CONCEPT of improvement during presentations

### What It Does:
- ❌ Does NOT generate real code
- ❌ Does NOT call real APIs
- ❌ Does NOT store in Neo4j
- ✅ Shows simulated workflow
- ✅ Displays hardcoded scores (93.5 → 95.5 → 97.2)
- ✅ Fast execution (5-7 minutes with pauses)
- ✅ Pretty color output
- ✅ Perfect for presenting

### Use When:
- Presenting to stakeholders
- Demoing the concept
- Teaching how it works
- Time is limited
- Don't need validation

### Run:
```bash
python3 demo/demo_presentation.py
```

### Output:
- Terminal output only
- No files generated
- No database changes
- Nothing to validate

---

## 2. `demo_real.py` - For Validation

**Purpose:** Generate REAL code that can be validated

### What It Does:
- ✅ Generates real code using real LLMs
- ✅ Calls Claude Sonnet 4.5, GPT-5 Pro
- ✅ Stores patterns in Neo4j
- ✅ Gets real scores from Galileo
- ✅ Outputs validatable code files
- ⏱️ Slower (3-5 minutes per request)
- 💰 Uses API credits (~$0.24 total)

### Use When:
- Need to validate actual code
- Want to see real improvement
- Demonstrating to technical audience
- Building real knowledge base
- Testing the system

### Run:
```bash
python3 demo/demo_real.py
```

### Output:
```
demo_output/demo_YYYYMMDD_HHMMSS/
├── request_01/
│   ├── architecture.md        ← Real architecture doc
│   ├── implementation.py      ← Real Python code
│   └── results.json           ← Real scores
├── request_02/
│   ├── architecture.md
│   ├── implementation.py
│   └── results.json
└── request_03/
    ├── architecture.md
    ├── implementation.py
    └── results.json
```

### Validation:
1. **Check generated code:**
   ```bash
   cat demo_output/*/request_01/implementation.py
   ```

2. **View Neo4j patterns:**
   - Open: http://localhost:7474
   - Query: `MATCH (p:CodePattern) WHERE p.demo = true RETURN p`

3. **Check Galileo scores:**
   - Visit: https://app.galileo.ai
   - Check project: codeswarm-demo-req1, req2, req3

---

## 3. `demo.py` - Full Workflow with Vision

**Purpose:** Complete demo with sketch-to-code vision support

### What It Does:
- ✅ Full workflow including Vision Agent
- ✅ Processes image sketches
- ✅ Generates real code
- ✅ All 5 agents (including vision)
- ⏱️ Slower (full workflow)

### Use When:
- Demoing vision capabilities
- Have a sketch/mockup image
- Want complete end-to-end flow
- Building from visual designs

### Run:
```bash
python3 demo/demo.py path/to/sketch.jpg
```

---

## Comparison Table

| Feature | demo_presentation.py | demo_real.py | demo.py |
|---------|---------------------|--------------|---------|
| Real code generation | ❌ | ✅ | ✅ |
| Real API calls | ❌ | ✅ | ✅ |
| Neo4j storage | ❌ | ✅ | ✅ |
| Galileo scoring | ❌ | ✅ | ✅ |
| Output files | ❌ | ✅ | ✅ |
| Validatable | ❌ | ✅ | ✅ |
| Fast execution | ✅ | ❌ | ❌ |
| Pretty output | ✅ | ✅ | ❌ |
| Shows improvement | ✅ (simulated) | ✅ (real) | ❌ |
| Vision support | ❌ | ❌ | ✅ |
| API cost | $0 | ~$0.24 | ~$0.10 |
| Best for | Presentations | Validation | Vision demos |

---

## Recommended Demo Flow

### For Investors/Executives:
1. **Start:** demo_presentation.py (show concept)
2. **Then:** Show pre-generated code from demo_real.py
3. **Finally:** Show Neo4j graph with real patterns

### For Technical Audience:
1. **Start:** demo_real.py (generate real code)
2. **During:** Explain architecture while code generates
3. **After:** Validate code, show Neo4j, check Galileo

### For Hackathon Judges:
1. **Start:** demo.py with sketch image
2. **Show:** Real code being generated
3. **Validate:** Run the generated code
4. **Prove:** Show Neo4j patterns and scores

---

## Common Questions

### "Which one should I use for my presentation tomorrow?"

**Answer:** `demo_presentation.py`
- Fast, reliable, shows the concept perfectly
- Pre-run `demo_real.py` beforehand to have code to show

### "I need to prove the code quality actually improves"

**Answer:** `demo_real.py`
- Generates real code with real scores
- Can validate every file
- Shows actual improvement in Neo4j

### "I have a sketch and want to show sketch-to-code"

**Answer:** `demo.py path/to/sketch.jpg`
- Full vision pipeline
- Sketch → Architecture → Code
- Production-ready output

### "What if my demo presentation crashes?"

**Answer:** Have backups ready:
1. Pre-run `demo_real.py` and save output
2. Take screenshots of the process
3. Have code files ready to show
4. Fallback to `demo_presentation.py` (never crashes)

---

## Output Location Guide

### demo_presentation.py:
```
No files generated
Terminal output only
```

### demo_real.py:
```
demo_output/
└── demo_20251018_153000/
    ├── request_01/
    │   ├── architecture.md
    │   ├── implementation.py
    │   └── results.json
    ├── request_02/
    │   └── ...
    └── request_03/
        └── ...
```

### demo.py:
```
output/
└── generated_code.txt  (combined output)
```

---

## How to Validate Results

### After demo_real.py:

**1. Check Code Files:**
```bash
# View architecture
cat demo_output/*/request_01/architecture.md

# View implementation
cat demo_output/*/request_01/implementation.py

# Check scores
cat demo_output/*/request_01/results.json
```

**2. Verify Neo4j Storage:**
```bash
# Open Neo4j Browser
open http://localhost:7474

# Run this query:
MATCH (p:CodePattern)
WHERE p.demo = true
RETURN p.id, p.avg_score, p.task
ORDER BY p.timestamp DESC
```

**3. Confirm Galileo Scores:**
```bash
# Check Galileo projects
open https://app.galileo.ai

# Look for:
# - codeswarm-demo-req1
# - codeswarm-demo-req2
# - codeswarm-demo-req3
```

**4. Test Generated Code:**
```bash
# Copy implementation to test
cp demo_output/*/request_01/implementation.py test_auth.py

# Check syntax
python3 -m py_compile test_auth.py

# Check imports
python3 -c "import ast; ast.parse(open('test_auth.py').read())"
```

---

## Cleanup After Demo

### To remove demo data:

**1. Delete generated files:**
```bash
rm -rf demo_output/demo_*/
```

**2. Remove Neo4j demo patterns:**
```cypher
// In Neo4j Browser:
MATCH (p:CodePattern)
WHERE p.demo = true
DETACH DELETE p
```

**3. Galileo projects stay** (for reference)

---

## Quick Reference

**Need it now?**
- Fast demo: `python3 demo/demo_presentation.py`
- Real code: `python3 demo/demo_real.py`
- With image: `python3 demo/demo.py sketch.jpg`

**Want validation?**
- Check: `demo_output/*/request_*/`
- Neo4j: http://localhost:7474
- Galileo: https://app.galileo.ai

**Clean up?**
- Files: `rm -rf demo_output/demo_*/`
- Neo4j: `MATCH (p:CodePattern) WHERE p.demo = true DETACH DELETE p`

---

## Summary

- **Presenting?** → Use `demo_presentation.py` (safe, fast, pretty)
- **Validating?** → Use `demo_real.py` (real code, real scores)
- **Vision demo?** → Use `demo.py` (sketch-to-code)

All demos show CodeSwarm's value, just in different ways!
