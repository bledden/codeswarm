# Browser Use - Debug Information for Support

## Issue Summary

**Problem**: All Browser Use tasks fail with `ERR_TUNNEL_CONNECTION_FAILED` error

**Status**: Tasks finish quickly (8-18 seconds) but always report `is_success: False`

**Error Message**:
```
"I attempted to go to example.com, but the browser reported that the site
could not be reached due to an ERR_TUNNEL_CONNECTION_FAILED error."
```

---

## API Key Info

**API Key**: `bu_GySOPbgmUAnVg2IoUCmjO7LWlU0CRTQZ79oSBAKkFuc`

**SDK Version**: `browser-use-sdk==2.0.4`

**Python Version**: 3.9

**Environment**: macOS (Darwin 24.6.0)

---

## Minimal Reproduction

```python
from browser_use_sdk import BrowserUse
import os
import time

# Initialize client
client = BrowserUse(api_key="bu_GySOPbgmUAnVg2IoUCmjO7LWlU0CRTQZ79oSBAKkFuc")

# Create simplest possible task
task = client.tasks.create_task(
    task="Go to example.com",
    start_url="https://www.example.com",
    max_steps=1
)

# Wait for completion
time.sleep(10)
status = client.tasks.get_task(task_id=task.id)

print(f"Status: {status.status}")           # "finished"
print(f"Success: {status.is_success}")      # False
print(f"Output: {status.output}")           # ERR_TUNNEL_CONNECTION_FAILED
```

**Result**:
- Status: `finished` (not `completed`)
- Success: `False`
- Output: `"ERR_TUNNEL_CONNECTION_FAILED"`

---

## Test Results

### Test 1: Simple Navigation (example.com)
```
Task: "Go to example.com"
URL: https://www.example.com
Result: ❌ ERR_TUNNEL_CONNECTION_FAILED
Time: 8 seconds
```

### Test 2: Google Search
```
Task: "Search Google for 'Python' and return the first URL"
URL: https://www.google.com
Result: ❌ Finished with is_success=False
Time: 18 seconds
```

### Test 3: Documentation Scraping
```
Task: "Search Google for 'FastAPI tutorial documentation' and extract URLs"
URL: https://www.google.com/search?q=...
Result: ❌ Timeout (never completes)
Time: 30+ seconds
```

---

## Questions for Browser Use Team

### 1. API Key / Account Status
- ✅ Is this API key valid and active?
- ✅ Are there any rate limits or restrictions?
- ✅ Is the account in good standing?

### 2. Tunnel Connection Error
- ❌ Why are we getting `ERR_TUNNEL_CONNECTION_FAILED`?
- ❌ Is this a known issue with the cloud service?
- ❌ Is there a proxy/network configuration issue?
- ❌ Do we need to whitelist any IPs or configure tunneling?

### 3. Task Completion
- ❌ Why do tasks finish with `status="finished"` but `is_success=False`?
- ❌ What's the difference between `"finished"` and `"completed"`?
- ❌ Should we be checking `is_success` instead of `status`?

### 4. Best Practices
- ⚠️ What's the expected completion time for simple tasks?
- ⚠️ Should we use different parameters for documentation scraping?
- ⚠️ Is there a better way to search and extract URLs?
- ⚠️ Are there example tasks that work reliably?

### 5. Our Use Case
**What we're trying to do**:
- Search for documentation (e.g., "FastAPI tutorial docs")
- Extract top 3 documentation URLs from search results
- Scrape documentation text and code examples
- Use as context for AI code generation

**Current approach**:
```python
task = client.tasks.create_task(
    task=f"Search Google for '{query}' and extract the top 3 result URLs",
    start_url=f"https://www.google.com/search?q={query}",
    max_steps=10
)
```

**Question**: Is this the right approach, or should we use a different method?

---

## Expected vs Actual Behavior

### Expected ✅
```python
status = client.tasks.get_task(task_id=task.id)
# After 10-30 seconds:
status.status == "completed"  # or "finished"?
status.is_success == True
status.output == "https://fastapi.tiangolo.com/..."  # URLs found
```

### Actual ❌
```python
status = client.tasks.get_task(task_id=task.id)
# After 8-18 seconds:
status.status == "finished"
status.is_success == False
status.output == "ERR_TUNNEL_CONNECTION_FAILED error"
```

---

## System Information

```
OS: macOS (Darwin 24.6.0)
Python: 3.9
SDK: browser-use-sdk==2.0.4
Also installed: browserbase==1.4.0

Network: Standard internet connection (no corporate proxy)
Location: United States
```

---

## What We Need

**Immediate**:
1. ✅ Confirmation that API key is valid
2. ❌ Fix for tunnel connection errors
3. ❌ Working example of search + URL extraction

**Long-term**:
1. Reliable documentation scraping (3-5 second response time)
2. Ability to extract URLs from search results
3. Ability to scrape documentation pages

---

## Current Workaround

We've implemented a fallback to Tavily API when Browser Use fails:

```python
# Try Browser Use first (30 second timeout)
try:
    results = await browser_use.search_and_scrape(query)
except:
    # Fall back to Tavily
    results = await tavily.search(query)
```

This works, but we'd prefer to use Browser Use as the primary service.

---

## Files for Reference

- **Integration code**: `src/integrations/browser_use_client.py`
- **Test script**: `test_minimal_browser_use.py`
- **Full logs**: Available on request

---

## Quick Test Command

To reproduce the issue:

```bash
python3 << 'EOF'
from browser_use_sdk import BrowserUse
import time

client = BrowserUse(api_key="bu_GySOPbgmUAnVg2IoUCmjO7LWlU0CRTQZ79oSBAKkFuc")
task = client.tasks.create_task(
    task="Go to example.com",
    start_url="https://www.example.com",
    max_steps=1
)

time.sleep(10)
status = client.tasks.get_task(task_id=task.id)
print(f"Success: {status.is_success}")  # Should be True, but is False
print(f"Output: {status.output}")       # Shows tunnel error
EOF
```

**Expected**: Success=True, Output="Navigated to example.com"
**Actual**: Success=False, Output="ERR_TUNNEL_CONNECTION_FAILED"
