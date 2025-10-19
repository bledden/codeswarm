#!/bin/bash
# Security check script - scans for accidentally exposed API keys

echo "🔒 Checking for exposed API keys..."
echo ""

FOUND=0

# Check for common API key patterns (excluding .env and .env.example)
echo "Scanning Python files..."
if grep -r "sk-or-v1-\|sk-proj-\|sk_test_\|dtn_\|bu_\|tvly-\|gal_" \
    --include="*.py" \
    --exclude-dir=".git" \
    --exclude-dir="venv" \
    --exclude-dir="__pycache__" \
    . 2>/dev/null | grep -v "your_.*_key_here" | grep -v ".env"; then
    echo "❌ Found potential API keys in Python files!"
    FOUND=1
else
    echo "✅ No API keys found in Python files"
fi

echo ""
echo "Scanning markdown files..."
if grep -r "sk-or-v1-\|sk-proj-\|sk_test_\|dtn_\|bu_\|tvly-" \
    --include="*.md" \
    --exclude-dir=".git" \
    --exclude="README.md" \
    --exclude="SETUP_GUIDE.md" \
    . 2>/dev/null | grep -v "your_.*_key_here" | grep -v "xxxxx"; then
    echo "❌ Found potential API keys in markdown files!"
    FOUND=1
else
    echo "✅ No API keys found in markdown files"
fi

echo ""
echo "Checking .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo "✅ .env is in .gitignore"
else
    echo "❌ .env is NOT in .gitignore!"
    FOUND=1
fi

echo ""
if [ $FOUND -eq 0 ]; then
    echo "✅ Security check passed - no exposed API keys found"
    exit 0
else
    echo "❌ Security issues found - please review and fix"
    exit 1
fi
