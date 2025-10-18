# Quick Prompt Change Guide

Want to use different demo prompts? Here's how:

## The File

**Edit:** `demo/demo_real.py`

## The Lines

Search for these sections (around lines 377-416):

### Request 1 (Line ~378)
```python
request1 = RealDemoRequest(
    request_num=1,
    task="Build a FastAPI user authentication endpoint with password hashing using bcrypt",  # ← CHANGE THIS
    output_dir=output_dir
)
```

### Request 2 (Line ~394)
```python
request2 = RealDemoRequest(
    request_num=2,
    task="Build authentication API with JWT access tokens and refresh tokens",  # ← CHANGE THIS
    output_dir=output_dir
)
```

### Request 3 (Line ~409)
```python
request3 = RealDemoRequest(
    request_num=3,
    task="Build production-ready authentication with JWT, rate limiting, and account lockout protection",  # ← CHANGE THIS
    output_dir=output_dir
)
```

## Recommended Replacements

### E-Commerce Demo (Most Impressive)

**Request 1:**
```python
task="Build a REST API for an e-commerce product catalog with search, filtering, and price ranges using FastAPI and PostgreSQL",
```

**Request 2:**
```python
task="Build a shopping cart API with product quantities, discount codes, tax calculation, and inventory checking",
```

**Request 3:**
```python
task="Build a complete order management system with payment processing, order tracking, and email notifications",
```

**Why:** Shows building a real production system incrementally

### API Evolution Demo (Most Educational)

**Request 1:**
```python
task="Build a REST API for managing blog posts with CRUD operations, user authentication, and full-text search",
```

**Request 2:**
```python
task="Build a REST API for managing user comments with nested replies, voting system, and spam detection",
```

**Request 3:**
```python
task="Build a GraphQL API with real-time subscriptions for collaborative document editing with conflict resolution",
```

**Why:** Shows architectural evolution (REST → GraphQL)

## Quick Edit Commands

```bash
# Option 1: Edit directly
nano demo/demo_real.py
# Jump to line 378, change prompts, save

# Option 2: Using sed (e-commerce example)
cd /Users/bledden/Documents/codeswarm

# Backup first
cp demo/demo_real.py demo/demo_real.py.backup

# Replace Request 1 prompt
sed -i '' '378s/.*/    task="Build a REST API for an e-commerce product catalog with search, filtering, and price ranges using FastAPI and PostgreSQL",/' demo/demo_real.py

# Replace Request 2 prompt  
sed -i '' '394s/.*/    task="Build a shopping cart API with product quantities, discount codes, tax calculation, and inventory checking",/' demo/demo_real.py

# Replace Request 3 prompt
sed -i '' '409s/.*/    task="Build a complete order management system with payment processing, order tracking, and email notifications",/' demo/demo_real.py
```

## After Changing

Run the demo:
```bash
python3 demo/demo_real.py
```

Check output:
```bash
ls demo_output/demo_*/request_*/
cat demo_output/demo_*/request_01/implementation.py
```

## Restore Original

```bash
cp demo/demo_real.py.backup demo/demo_real.py
```

---

See [DEMO_PROMPTS.md](DEMO_PROMPTS.md) for more prompt ideas!
