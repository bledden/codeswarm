# WorkOS Quick Setup (2 Minutes)

## Required Variables (4 total)

You need **4 environment variables** per [WorkOS docs](https://workos.com/docs/authkit/vanilla/python/1-configure-your-project/set-secrets):

```bash
WORKOS_API_KEY=sk_live_...              # From dashboard
WORKOS_CLIENT_ID=client_...             # From dashboard
WORKOS_REDIRECT_URI=http://localhost:3000/callback
WORKOS_COOKIE_PASSWORD=<32_chars>       # Generate with openssl
```

---

## Quick Setup Steps

### 1. Get API Keys (1 min)
Go to [https://dashboard.workos.com/api-keys](https://dashboard.workos.com/api-keys)

Copy:
- API Key (starts with `sk_`)
- Client ID (starts with `client_`)

### 2. Generate Cookie Password (10 sec)
```bash
./generate_workos_cookie_password.sh
```

Or manually:
```bash
openssl rand -base64 24
```

### 3. Configure Redirect URI (30 sec)
1. Go to [https://dashboard.workos.com/redirects](https://dashboard.workos.com/redirects)
2. Click **Add Redirect**
3. Enter: `http://localhost:3000/callback`
4. Click **Save**

### 4. Update .env (30 sec)
```bash
# WorkOS - Team authentication
WORKOS_API_KEY=sk_live_paste_your_key_here
WORKOS_CLIENT_ID=client_paste_your_id_here
WORKOS_REDIRECT_URI=http://localhost:3000/callback
WORKOS_COOKIE_PASSWORD=paste_generated_password_here
```

### 5. Test (10 sec)
```bash
python3 -c "from src.integrations.workos_client import WorkOSAuthClient; w=WorkOSAuthClient(); print('✅ WorkOS configured!')"
```

---

## What You Get

✅ WorkOS client initializes
✅ Can generate OAuth URLs
✅ Can list organizations
⚠️ Workflow authentication still placeholder (see [WORKOS_AUTH_STATUS.md](WORKOS_AUTH_STATUS.md))

---

## Full Details

See [WORKOS_SETUP_COMPLETE.md](WORKOS_SETUP_COMPLETE.md) for:
- Detailed explanations
- Troubleshooting
- Production setup
- Complete OAuth flow implementation
