# 🚨 URGENT: Backend Deployment Required for India OTP Feature

## Changes Made
Latest commits add **India OTP requirement** - all logins from India or with username `india_user` must complete 2FA.

## Required Actions

### 1. Pull Latest Code
```bash
cd /path/to/backend
git pull origin main
```

### 2. Install New Dependency
```bash
pip install requests==2.32.3
# Or reinstall all requirements
pip install -r requirements.txt
```

### 3. Create India Test User (if not exists)
```bash
python create_india_user.py
```

### 4. Restart Backend Server
```bash
# Stop current server (Ctrl+C if running in terminal)

# Restart with:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or if using systemd/service:
sudo systemctl restart zt-backend
```

## What This Fixes

### Before (BROKEN):
- `india_user` logs in without OTP ❌
- India IP addresses bypass 2FA if device is known ❌

### After (FIXED):
- `india_user` **ALWAYS** requires OTP ✅
- Any login from India (country code: IN) **ALWAYS** requires OTP ✅
- Works regardless of device trust status ✅

## Testing

1. **Test with `india_user`:**
   ```
   Username: india_user
   Password: Test123!
   Expected: OTP screen ALWAYS shown
   ```

2. **Check Logs:**
   Look for these debug messages:
   ```
   [AUTH DEBUG] User: india_user, IP: xxx, Location: xxx, Country: XX
   [2FA] FORCING 2FA for India/india_user - Username: india_user, Country: XX
   [2FA] FINAL DECISION - require_2fa: True
   [RESPONSE] Returning OTP challenge for user: india_user
   [RESPONSE] OTP Response: status=otp, message=Two-factor authentication required
   ```

## Key Files Changed

1. `backend/main.py` - India detection + force 2FA logic
2. `backend/ml_engine_uae.py` - India risk scoring + VPN detection
3. `backend/requirements.txt` - Added `requests` library
4. `backend/requirements-render.txt` - Added `requests` library
5. `backend/create_india_user.py` - New script to create test user
6. `backend/create_demo_users.py` - Added `india_user` to demo users
7. `kiosk/src/components/LoginForm.tsx` - Send `user_agent` field

## Troubleshooting

### OTP Still Not Showing?

1. **Check backend is actually restarted:**
   ```bash
   curl http://localhost:8000/api/health
   # Should return current timestamp/version
   ```

2. **Check logs show new debug messages:**
   ```bash
   tail -f /path/to/logs
   # Should see [AUTH DEBUG], [2FA], [RESPONSE] messages
   ```

3. **Verify user exists:**
   ```bash
   python -c "from database import get_user; print(get_user('india_user'))"
   ```

4. **Clear browser cache:**
   - Open kiosk in incognito/private mode
   - Hard refresh (Ctrl+Shift+R)

5. **Check frontend is pointing to correct backend:**
   - Open browser DevTools (F12)
   - Network tab
   - Try login
   - Check request URL matches your backend

## Backend URL
Current: `https://wallpaper-pregnant-onion-supposed.trycloudflare.com`
(Cloudflare Tunnel - temporary URL)

## Contact
If issues persist after deployment, check:
- GitHub commits from Nov 20, 2025
- Commit messages starting with "Fix: India OTP..."
- All commits are pushed to `main` branch

---

**Status:** ⏳ Waiting for backend deployment
**Priority:** 🔴 HIGH - Feature not working in production until deployed
