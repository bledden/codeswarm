#!/bin/bash
# Phase 4 Feedback Loop Integration Test
# Simulates user providing feedback after code generation

echo "=== PHASE 4 FEEDBACK LOOP TEST ==="
echo "=== START: $(date '+%Y-%m-%d %H:%M:%S') ==="
echo ""

# Simulate interactive feedback using here-document
# Inputs:
# - Code quality: 5
# - Context quality: 2 (low score to trigger unhelpful doc identification)
# - Unhelpful docs: 1,3 (mark docs 1 and 3 as unhelpful)

python3.11 codeswarm.py --task "create a simple hello world HTML page" <<EOF
5
2
1,3
EOF

echo ""
echo "=== END: $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== Check for Phase 4 feedback prompts above ==="
