# WorkOS Complete Setup Guide

## Required Environment Variables

Based on [WorkOS AuthKit Documentation](https://workos.com/docs/authkit/vanilla/python/1-configure-your-project/set-secrets), you need **4 environment variables**:

### 1. WORKOS_API_KEY
- **What**: Your WorkOS API key (starts with `sk_`)
- **Where**: [WorkOS Dashboard → API Keys](https://dashboard.workos.com/api-keys)
- **Example**: `sk_live_abc123...`

### 2. WORKOS_CLIENT_ID
- **What**: Your WorkOS Client ID (starts with `client_`)
- **Where**: [WorkOS Dashboard → API Keys](https://dashboard.workos.com/api-keys)
- **Example**: `client_abc123...`

### 3. WORKOS_REDIRECT_URI
- **What**: Callback endpoint where WorkOS redirects after authentication
- **Where**: Configure in [WorkOS Dashboard → Redirects](https://dashboard.workos.com/redirects)
- **For local dev**: `http://localhost:3000/callback`
- **For production**: `https://yourdomain.com/auth/callback`

**IMPORTANT**: You must add this exact URL to your WorkOS Dashboard Redirects section!

### 4. WORKOS_COOKIE_PASSWORD
- **What**: 32-character password to encrypt session cookies
- **Generate**: Run this command:
  ```bash
  openssl rand -base64 24
  ```
- **Example**: `abc123def456ghi789jkl012mno345==`

---

## Step-by-Step Setup

### Step 1: Get API Credentials

1. Go to [WorkOS Dashboard](https://dashboard.workos.com)
2. Click **API Keys** in left sidebar
3. Copy your **API Key** (starts with `sk_`)
4. Copy your **Client ID** (starts with `client_`)

### Step 2: Configure Redirect URI

1. In WorkOS Dashboard, click **Redirects**
2. Click **Add Redirect**
3. Enter: `http://localhost:3000/callback`
4. Click **Save**

For production, also add your production callback URL.

### Step 3: Generate Cookie Password

Run in terminal:
```bash
openssl rand -base64 24
```

Copy the output (should be ~32 characters).

### Step 4: Update .env File

Open your `.env` file and add:

```bash
# WorkOS - Team authentication
WORKOS_API_KEY=sk_live_your_actual_key_here
WORKOS_CLIENT_ID=client_your_actual_id_here
WORKOS_REDIRECT_URI=http://localhost:3000/callback
WORKOS_COOKIE_PASSWORD=your_generated_password_here
```

### Step 5: Verify Configuration

Test that WorkOS client initializes:

```bash
python3 -c "
from src.integrations.workos_client import WorkOSAuthClient

try:
    workos = WorkOSAuthClient()
    print('✅ WorkOS configured successfully!')
    print(f'   Client ID: {workos.client_id[:20]}...')
    print(f'   Redirect URI: {workos.redirect_uri}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

---

## What Each Variable Does

### WORKOS_API_KEY
- Authenticates your app with WorkOS API
- Required for ALL WorkOS operations
- Keep this secret! Never commit to git

### WORKOS_CLIENT_ID
- Identifies your application to WorkOS
- Used in OAuth flow to know which app is requesting auth
- Safe to expose in frontend (used in auth URLs)

### WORKOS_REDIRECT_URI
- Where users are sent after logging in
- WorkOS will POST authentication code here
- Must match exactly what's in your Dashboard

### WORKOS_COOKIE_PASSWORD
- Encrypts session cookies on your server
- Prevents cookie tampering
- Must be 32+ characters for security

---

## Testing WorkOS Integration

### Test 1: Generate Auth URL

```bash
python3 -c "
from src.integrations.workos_client import WorkOSAuthClient

workos = WorkOSAuthClient()

# Generate OAuth URL
url = workos.get_authorization_url(provider='GoogleOAuth')
print(f'Auth URL: {url}')
print()
print('To test authentication:')
print('1. Visit the URL above')
print('2. Log in with Google')
print('3. You will be redirected to your callback URL')
print('4. Extract the code parameter from the URL')
"
```

### Test 2: List Organizations

```bash
python3 -c "
from src.integrations.workos_client import WorkOSAuthClient

workos = WorkOSAuthClient()

orgs = workos.list_organizations()
print(f'Organizations: {len(orgs)}')

for org in orgs:
    print(f'  - {org[\"name\"]} ({org[\"id\"]})')
"
```

### Test 3: Full Demo with WorkOS

```bash
python3 demo_full_integration.py
```

Should show:
```
✅ WorkOS initialized
   Client ID: client_abc123...
   Redirect URI: http://localhost:3000/callback
```

---

## Common Issues

### Issue 1: "No redirect URI provided"

**Error**:
```
ValueError: No redirect URI provided. Set WORKOS_REDIRECT_URI in .env
```

**Solution**:
1. Add `WORKOS_REDIRECT_URI=http://localhost:3000/callback` to `.env`
2. Configure the same URL in WorkOS Dashboard → Redirects

### Issue 2: "Redirect URI not configured"

**Error** (when using auth URL):
```
WorkOS Error: Redirect URI not configured for this client
```

**Solution**:
1. Go to [WorkOS Dashboard → Redirects](https://dashboard.workos.com/redirects)
2. Click **Add Redirect**
3. Enter exact URL from your `.env` file
4. Click **Save**

### Issue 3: Cookie password too short

**Error**:
```
ValueError: Cookie password must be at least 32 characters
```

**Solution**:
```bash
# Generate new password
openssl rand -base64 24

# Add to .env
WORKOS_COOKIE_PASSWORD=<paste_generated_password>
```

### Issue 4: Users not showing in Dashboard

**Cause**: Current implementation doesn't actually create users

**Explanation**:
- The workflow just prints "authenticated" but doesn't call WorkOS APIs
- To see real users, you need to:
  1. Set up Directory Sync (syncs from Google Workspace/Azure AD)
  2. Invite users manually in Dashboard
  3. Complete OAuth flow to create authenticated sessions

**See**: [docs/WORKOS_AUTH_STATUS.md](WORKOS_AUTH_STATUS.md) for full details on what's implemented vs. what's not.

---

## What's Actually Working

Based on the current implementation:

| Feature | Status | Notes |
|---------|--------|-------|
| Client Initialization | ✅ Working | Loads all 4 env vars |
| Generate Auth URLs | ✅ Working | Creates real OAuth URLs |
| List Organizations | ✅ Working | Real API call |
| Get User by Email | ✅ Working | If Directory Sync enabled |
| **Workflow Authentication** | ❌ Placeholder | Just prints success |
| Complete OAuth Flow | ⚠️ Partial | Need web server for callback |

---

## Production Setup Checklist

For a production deployment:

- [ ] Get production WorkOS API key
- [ ] Get production Client ID
- [ ] Set production redirect URI (`https://yourdomain.com/auth/callback`)
- [ ] Generate strong cookie password (32+ chars)
- [ ] Add redirect URI to WorkOS Dashboard
- [ ] Configure SSL/HTTPS for callback endpoint
- [ ] Set up web server to handle `/callback` route
- [ ] Implement session storage (Redis, database)
- [ ] Add session expiration handling
- [ ] Configure organization settings
- [ ] Set up Directory Sync (optional)
- [ ] Test complete OAuth flow
- [ ] Add error handling for failed auth
- [ ] Configure logout endpoint
- [ ] Add session refresh logic

---

## Next Steps

### For Demo (Quick):
1. Add all 4 env vars to `.env`
2. Configure redirect URI in Dashboard
3. Run `python3 demo_full_integration.py`
4. Client will initialize successfully ✅
5. Note: Actual authentication still placeholder

### For Production (Complete):
1. Complete all env var setup
2. Implement web server for callback endpoint
3. Add code exchange logic (see WorkOS docs)
4. Store session tokens
5. Verify tokens on each request
6. Add logout functionality
7. Handle token refresh
8. Test full user flow

---

## Useful Links

- [WorkOS Dashboard](https://dashboard.workos.com)
- [API Keys](https://dashboard.workos.com/api-keys)
- [Redirect URIs](https://dashboard.workos.com/redirects)
- [AuthKit Python Docs](https://workos.com/docs/authkit/vanilla/python)
- [WorkOS Python SDK](https://github.com/workos/workos-python)

---

## Summary

**Minimum Required for Demo**:
```bash
# .env file
WORKOS_API_KEY=sk_live_...
WORKOS_CLIENT_ID=client_...
WORKOS_REDIRECT_URI=http://localhost:3000/callback
WORKOS_COOKIE_PASSWORD=<32_char_password>
```

**Generate cookie password**:
```bash
openssl rand -base64 24
```

**Configure in Dashboard**:
- Add redirect URI to WorkOS Dashboard → Redirects

**Test**:
```bash
python3 demo_full_integration.py
```

**Status**: Client initializes ✅, but workflow doesn't actually authenticate users yet ⚠️

For real authentication, see [WORKOS_AUTH_STATUS.md](WORKOS_AUTH_STATUS.md).
