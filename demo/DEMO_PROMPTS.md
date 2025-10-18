# Powerful Demo Prompts

Prompts designed to showcase CodeSwarm's self-improving capabilities beyond basic authentication.

---

## Current Demo (Authentication Focus)

**File:** `demo/demo_real.py` (lines 377-416)

**Current prompts:**
1. "Build a FastAPI user authentication endpoint with password hashing using bcrypt"
2. "Build authentication API with JWT access tokens and refresh tokens"
3. "Build production-ready authentication with JWT, rate limiting, and account lockout protection"

**What it shows:**
- ✅ Pattern reuse
- ✅ Score improvement
- ❌ Limited domain variety
- ❌ Doesn't show knowledge transfer across different problem types

---

## Better Demo Prompts (Showcase Self-Improvement)

### Option 1: Progressive E-Commerce Features
**Shows:** Building on previous patterns to create increasingly complex features

**Request 1 (Baseline):**
```
Build a product catalog API with search and filtering using FastAPI and PostgreSQL
```
**Expected:** ~92-94/100 (cold start)

**Request 2 (Learning):**
```
Build a shopping cart system with product quantities and price calculations
```
**Expected:** ~94-96/100 (reuses database patterns, API structure)
**Why better:** Cart can reference product catalog patterns

**Request 3 (Mastery):**
```
Build a complete checkout flow with inventory management, payment validation, and order history
```
**Expected:** ~96-98/100 (synthesizes catalog + cart + adds new features)
**Why better:** Shows how all 3 patterns compound into complex workflow

**Improvement trajectory:** Product API → Cart → Full Checkout
**Shows:** Domain knowledge accumulation

---

### Option 2: Data Processing Pipeline Evolution
**Shows:** Learning from mistakes and improving data handling

**Request 1 (Baseline):**
```
Build a CSV file processor that reads sales data and calculates daily totals
```
**Expected:** ~91-93/100 (simple file processing)

**Request 2 (Error Handling):**
```
Build a batch data processor that handles multiple CSV files with error logging and retry logic
```
**Expected:** ~94-96/100 (improves on error handling from Request 1)
**Why better:** Security agent will catch missing error handling from R1

**Request 3 (Production Scale):**
```
Build a real-time data pipeline with streaming ingestion, validation, and anomaly detection
```
**Expected:** ~97-99/100 (combines all learned patterns)
**Why better:** Shows evolution from simple → batch → real-time

**Improvement trajectory:** Single file → Batch → Streaming
**Shows:** Complexity scaling with maintained quality

---

### Option 3: API Design Evolution (BEST FOR DEMOS)
**Shows:** Learning better architecture patterns over time

**Request 1 (Baseline):**
```
Build a REST API for managing blog posts with CRUD operations
```
**Expected:** ~92-94/100 (standard CRUD)

**Request 2 (Enhanced):**
```
Build a REST API for managing user comments with nested replies, voting, and moderation
```
**Expected:** ~95-97/100 (learns from post structure, adds complexity)
**Why better:** Architecture agent will reuse post patterns for comments

**Request 3 (Advanced):**
```
Build a GraphQL API with real-time subscriptions for a collaborative document editing system
```
**Expected:** ~97-99/100 (best of REST patterns + new GraphQL)
**Why better:** Shows learning transfer from REST → GraphQL

**Improvement trajectory:** REST CRUD → Complex REST → GraphQL
**Shows:** API pattern evolution and knowledge transfer

---

### Option 4: Machine Learning Pipeline
**Shows:** Building ML infrastructure incrementally

**Request 1 (Baseline):**
```
Build a data preprocessing pipeline for cleaning and normalizing customer data
```
**Expected:** ~91-93/100

**Request 2 (Feature Engineering):**
```
Build a feature engineering system that creates time-series features and handles missing values
```
**Expected:** ~94-96/100 (reuses preprocessing patterns)

**Request 3 (Full ML Pipeline):**
```
Build an end-to-end ML pipeline with preprocessing, training, validation, and model serving
```
**Expected:** ~97-99/100 (combines all learned patterns)

**Improvement trajectory:** Preprocess → Features → Full Pipeline
**Shows:** ML knowledge accumulation

---

## RECOMMENDED: Option 3 (API Evolution)

### Why This is Best for Demos:

1. **Clear progression:** REST → Enhanced REST → GraphQL
2. **Universal appeal:** Everyone understands APIs
3. **Visible improvement:** Each request builds on previous
4. **Diverse agents:**
   - Architecture evolves from CRUD → nested → real-time
   - Security learns authentication → authorization → real-time security
   - Testing grows from unit → integration → subscription tests

### Modified demo_real.py prompts:

```python
# Request 1: Basic REST API
request1 = RealDemoRequest(
    request_num=1,
    task="Build a REST API for managing blog posts with CRUD operations, user authentication, and search",
    output_dir=output_dir
)

# Request 2: Enhanced REST with relationships
request2 = RealDemoRequest(
    request_num=2,
    task="Build a REST API for managing user comments with nested replies, voting system, and spam detection",
    output_dir=output_dir
)

# Request 3: Advanced GraphQL
request3 = RealDemoRequest(
    request_num=3,
    task="Build a GraphQL API with real-time subscriptions for collaborative document editing with conflict resolution",
    output_dir=output_dir
)
```

---

## Why Current Demo is Limited

**Current (Auth-focused):**
```
Request 1: Build auth API
Request 2: Add JWT to auth API
Request 3: Add rate limiting to auth API
```
**Problem:** All same domain, incremental features only

**Better (API evolution):**
```
Request 1: Build blog post API (new domain)
Request 2: Build comment API (related but different)
Request 3: Build GraphQL API (totally different approach)
```
**Benefit:** Shows knowledge transfer across domains!

---

## Prompts That Show Specific Features

### Show Browser Use in Action:
```
Build a REST API using the latest FastAPI 0.115.0 features for async dependencies and lifespan events
```
**Why:** Forces Browser Use to scrape latest FastAPI docs

### Show Quality Gate:
```
Build a simple user registration form (intentionally vague)
```
**Why:** Vague prompt → low initial score → improvement loop kicks in

### Show Vision Agent:
```
Convert this sketch of a dashboard into a React component with charts and metrics
```
**Why:** Shows sketch-to-code capabilities (use with demo.py)

### Show Security Agent:
```
Build a file upload API that accepts user images
```
**Why:** Security agent will catch injection risks, path traversal, size limits

### Show Team Knowledge (with WorkOS):
```
Developer 1: Build OAuth login with Google
Developer 2: Build OAuth login with Microsoft
```
**Why:** Dev 2 gets Dev 1's patterns automatically

---

## How to Customize demo_real.py

**File:** `demo/demo_real.py`

**Lines to change:** 377-416

**Before:**
```python
request1 = RealDemoRequest(
    request_num=1,
    task="Build a FastAPI user authentication endpoint...",
    output_dir=output_dir
)
```

**After (for API evolution demo):**
```python
request1 = RealDemoRequest(
    request_num=1,
    task="Build a REST API for managing blog posts with CRUD operations, user authentication, and full-text search",
    output_dir=output_dir
)

# ... similar changes for request2 and request3
```

---

## Ultimate Demo Prompt Set (Wow Factor)

For maximum impact, show these 3 in sequence:

### Request 1: Simple E-Commerce Product API
```
Build a REST API for an e-commerce product catalog with search, filtering by category, and price ranges using FastAPI and PostgreSQL
```
**Expected:** 92-94/100
**Teaches:** Basic REST, database design, query optimization

### Request 2: Shopping Cart with Business Logic
```
Build a shopping cart API with product quantities, discount codes, tax calculation, and inventory checking
```
**Expected:** 95-97/100 (+3-5 points)
**Reuses:** Product schema, database patterns, API structure
**Adds:** Business logic, calculations, validation

### Request 3: Complete Order Management System
```
Build a complete order management system with payment processing, order status tracking, email notifications, and admin dashboard
```
**Expected:** 97-99/100 (+5-7 points from baseline)
**Synthesizes:** Products + Cart + new payment features
**Shows:** How 90+ patterns compound into production system

**Result:** Viewers see a complete e-commerce backend built in 3 iterations with visible quality improvement!

---

## Quick Change Guide

Want to use different prompts? Edit this file:
```bash
nano demo/demo_real.py
```

Go to lines **377-416** and replace the `task=` strings:

```python
# Line ~378: Request 1
task="YOUR NEW PROMPT HERE",

# Line ~394: Request 2
task="YOUR NEW PROMPT HERE",

# Line ~409: Request 3
task="YOUR NEW PROMPT HERE",
```

Save and run:
```bash
python3 demo/demo_real.py
```

---

## Testing Your New Prompts

Before the real demo:

1. **Test individually:**
   ```bash
   # Just Request 1
   # Edit demo_real.py to comment out requests 2 & 3
   python3 demo/demo_real.py
   ```

2. **Check output quality:**
   ```bash
   cat demo_output/*/request_01/implementation.py
   # Is the code good? Adjust prompt if needed.
   ```

3. **Verify improvement:**
   ```bash
   # Check scores in results.json
   cat demo_output/*/request_*/results.json | grep avg_score
   # Should see: 92 → 95 → 97 progression
   ```

---

## Summary

**Current demo:** Authentication → JWT → Rate limiting
**Better demo:** Blog API → Comment API → GraphQL API

**Why better:**
- ✅ Shows domain knowledge transfer
- ✅ More impressive progression
- ✅ Broader appeal
- ✅ Demonstrates architectural evolution

**Best prompts:** Option 3 (API Evolution) or Ultimate Demo (E-Commerce)

**File to edit:** `demo/demo_real.py` (lines 377-416)
