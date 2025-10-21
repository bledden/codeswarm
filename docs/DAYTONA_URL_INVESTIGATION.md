# Daytona Deployment URL Investigation

**Date**: 2025-10-21
**Issue**: Deployment URLs return 400 "no IP address found. Is the Sandbox started?" error
**Status**: Under Investigation

---

## Problem Description

When CodeSwarm deploys code to Daytona, it successfully:
1. ✅ Creates workspace
2. ✅ Uploads files
3. ✅ Starts server command (`python3 -m http.server 3000`)
4. ✅ Gets preview URL
5. ❌ BUT: URL returns 400 error when accessed

**Error Message**:
```json
{
  "statusCode": 400,
  "message": "bad request: no IP address found. Is the Sandbox started?",
  "code": "BAD_REQUEST",
  "timestamp": "2025-10-21T06:15:02.263640155Z",
  "path": "/sandboxes/9d58a476-e537-4da5-9075-8511724fe3a6/toolbox/proxy/3000/",
  "method": "GET"
}
```

---

## Current Deployment Flow

From [src/integrations/daytona_client.py](../src/integrations/daytona_client.py#L232-L335):

```python
# 1. Create workspace
workspace_id = await daytona_client.create_workspace()

# 2. Upload files using SDK
sandbox = daytona_sdk.get(workspace_id)
for file in files:
    sandbox.files.upload(file, content)

# 3. Execute server command
result = sandbox.process.exec("python3 -m http.server 3000")
# Note: This times out for long-running servers (expected)

# 4. Get preview URL
preview_url = await get_preview_url(workspace_id, port=3000)
# Returns: https://3000-{workspace_id}.proxy.daytona.works

# 5. Return URL to user
return {"url": preview_url}
```

**The Problem**: Step 3 times out (expected for servers), but the sandbox may not actually keep the server process running after the timeout.

---

## Root Cause Hypotheses

### Hypothesis 1: Process Dies After Timeout
- `sandbox.process.exec()` times out for long-running commands
- Daytona may kill the process after timeout
- Sandbox goes into stopped state
- Proxy can't find IP because sandbox isn't running

### Hypothesis 2: Sandbox Lifecycle Issue
- Sandbox created but not fully "started"
- Process runs but sandbox state != "running"
- Daytona proxy requires sandbox in specific state

### Hypothesis 3: Port Binding Delay
- Server process starts but hasn't bound to port 3000 yet
- Proxy checks port immediately, finds nothing
- Need to wait for port to be ready before returning URL

---

## Potential Solutions (In Order of Likelihood)

### Solution 1: Use Daytona Sessions API ⭐ (Most Likely)
**From Daytona Docs**: https://www.daytona.io/docs/process-code-execution/

Daytona SDK has `process.create_session()` for long-running processes:

```python
# Create a session for long-running server
session_id = f"server-{workspace_id[:8]}"
sandbox.process.create_session(session_id)

# Run command in session (doesn't timeout)
sandbox.process.exec_in_session(session_id, "python3 -m http.server 3000")

# Session keeps process alive even after SDK disconnects
```

**Benefits**:
- Designed specifically for long-running processes
- Process survives SDK disconnection
- Can list/monitor sessions later

**Risks**:
- Need to verify exact API (docs show `create_session` but not full usage)
- May require different SDK method signature

**Status**: ⏳ NEEDS TESTING - Don't implement until API verified

---

### Solution 2: Use `nohup` Command ⭐
**Standard Linux approach** for background processes:

```python
# Wrap server command in nohup
nohup_command = f"nohup {run_command} > /tmp/server.log 2>&1 &"
result = sandbox.process.exec(nohup_command)
```

**Benefits**:
- Standard Unix/Linux pattern
- Process survives terminal disconnect
- Logs captured to /tmp/server.log

**Risks**:
- May still timeout in SDK
- Sandbox needs to support nohup (should be available in most Linux images)

**Status**: ⏳ READY TO TEST - Can implement after verifying Solution 1 won't work

---

### Solution 3: Add Wait + Status Check
**Band-aid approach** - wait for sandbox to stabilize:

```python
# After starting server
await asyncio.sleep(5)  # Wait for process to stabilize

# Check sandbox status
status = await get_workspace_status(workspace_id)
if status['status'] != 'running':
    logger.warning("Sandbox not running yet")
    await asyncio.sleep(5)  # Wait more
```

**Benefits**:
- Easy to implement
- No SDK changes needed

**Risks**:
- Doesn't fix root cause
- Arbitrary wait times
- May not solve the problem

**Status**: ⏭️ SKIP - Only use if Solutions 1-2 fail

---

### Solution 4: Use Daytona REST API Directly
**Bypass SDK** and use REST endpoints:

```python
# Use REST API to start process in background
async with session.post(
    f"{api_url}/toolbox/{workspace_id}/process/start",
    json={
        "command": "python3 -m http.server 3000",
        "background": True  # Hypothetical parameter
    }
) as response:
    ...
```

**Benefits**:
- More control over process lifecycle
- May have different timeout behavior

**Risks**:
- REST API may not support background processes
- Would need to reverse-engineer API
- Less maintainable than SDK

**Status**: ⏭️ SKIP - Only if SDK solutions fail

---

### Solution 5: Use Daytona's Persistent Workspaces
**Keep workspace running** instead of creating new ones:

```python
# Reuse existing workspace instead of creating new
workspace_id = os.getenv("DAYTONA_PERSISTENT_WORKSPACE_ID")
sandbox = daytona.get(workspace_id)

# Deploy to persistent workspace
sandbox.files.upload(...)
sandbox.process.exec("pkill python3 && python3 -m http.server 3000")
```

**Benefits**:
- Workspace stays running between deployments
- No startup delay

**Risks**:
- Requires manual workspace creation
- State management between deployments
- Not scalable (one workspace per user?)

**Status**: ⏭️ SKIP - Doesn't match use case (need fresh envs)

---

## Investigation Plan

### Step 1: Verify Daytona SDK Session API
```bash
python3.11 -c "from daytona_sdk import Daytona; d = Daytona(); s = d.create(); print(dir(s.process))"
```

**Look for**:
- `create_session`
- `list_sessions`
- `delete_session`
- `exec_in_session` (or similar)

**If found**: Implement Solution 1
**If not found**: Move to Step 2

### Step 2: Test `nohup` Approach
```python
# In daytona_client.py
if "dev" in run_command or "http.server" in run_command:
    nohup_cmd = f"nohup {run_command} > /tmp/server.log 2>&1 &"
    sandbox.process.exec(nohup_cmd)
    await asyncio.sleep(3)  # Wait for startup
```

**Test**:
```bash
python3.11 codeswarm.py --task "create a simple hello world website"
# Check if URL works after deployment
```

### Step 3: Add Health Check
```python
# After getting preview_url
async def check_url_accessible(url, retries=3):
    for i in range(retries):
        try:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    return True
        except:
            await asyncio.sleep(2)
    return False

if not await check_url_accessible(preview_url):
    logger.warning("URL not accessible yet - may need 10-15 seconds")
```

---

## Testing Strategy

1. ✅ **Don't break existing functionality**
   - Test with non-server deployments first
   - Verify file uploads still work

2. ✅ **Incremental changes**
   - Test one solution at a time
   - Document results for each approach

3. ✅ **Measure success**
   - URL accessible immediately after deployment
   - Server remains running for > 5 minutes
   - Multiple deployments work consistently

4. ✅ **Failure modes**
   - What if sandbox crashes?
   - What if command fails?
   - What if port is already in use?

---

## Next Steps

**IMMEDIATE**:
1. Verify Daytona SDK session API exists and usage
2. Document exact method signatures
3. Choose Solution 1 or Solution 2 based on findings

**DO NOT**:
- Implement multiple solutions simultaneously
- Make experimental changes without verification
- Remove existing logic until proven better solution works

---

## References

- Daytona Docs: https://www.daytona.io/docs/process-code-execution/
- Daytona SDK GitHub: (need to find)
- Previous successful deployment: Test 997398 (logs show command executed but URL failed later)

---

**Status**: Waiting for proper investigation before implementing changes.
