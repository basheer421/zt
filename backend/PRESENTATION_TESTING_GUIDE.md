# 🎓 ZT-Verify Presentation Testing Guide

## Overview

This guide provides **3 real test scenarios** (Green/Yellow/Red) that you can demonstrate live during your university presentation.

---

## 📋 Quick Test Examples (JSON Format)

### 🟢 GREEN: UAE Employee (Allow - No 2FA)

**Scenario**: Employee logging in from Dubai office

```json
{
  "username": "john_doe",
  "password": "Test123!",
  "timestamp": "2025-10-26T10:30:00Z",
  "device_fingerprint": "uae_office_laptop_001",
  "ip_address": "5.62.61.123",
  "location": "Dubai, AE"
}
```

**Expected Result**:

- ✅ Status: `success`
- ✅ Risk Score: 5-10%
- ✅ No 2FA required
- ✅ Direct login allowed

**Why it's safe**:

- UAE country code (AE)
- Business hours (2:30 PM UAE time)
- Known device fingerprint

---

### 🟡 YELLOW: US Business Partner (Require 2FA)

**Scenario**: Partner logging in from United States

```json
{
  "username": "john_doe",
  "password": "Test123!",
  "timestamp": "2025-10-26T10:30:00Z",
  "device_fingerprint": "us_laptop_002",
  "ip_address": "8.8.8.8",
  "location": "New York, US"
}
```

**Expected Result**:

- ⚠️ Status: `otp`
- ⚠️ Risk Score: 40%
- ⚠️ 2FA required
- ⚠️ Message: "Two-factor authentication required"

**Why it requires 2FA**:

- Acceptable country (US) but not UAE
- Medium risk (30-70%)
- Unknown device from foreign location

---

### 🔴 RED: Russia Attack (Block/Strong Verification)

**Scenario**: Suspicious login from Russia

```json
{
  "username": "john_doe",
  "password": "Test123!",
  "timestamp": "2025-10-26T02:00:00Z",
  "device_fingerprint": "suspicious_device_003",
  "ip_address": "5.188.10.50",
  "location": "Moscow, RU"
}
```

**Expected Result**:

- 🚨 Status: `otp`
- 🚨 Risk Score: 80%
- 🚨 2FA required (would block in production)
- 🚨 High risk detected

**Why it's blocked**:

- High-risk country (Russia)
- Suspicious hours (6 AM UAE time)
- Unknown device from attack-prone location

---

## 🖥️ How to Test During Presentation

### Method 1: Using curl (Command Line Demo)

```bash
# GREEN: UAE Login
curl -X POST http://localhost:8000/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "Test123!",
    "timestamp": "2025-10-26T10:30:00Z",
    "device_fingerprint": "uae_office_laptop_001",
    "ip_address": "5.62.61.123",
    "location": "Dubai, AE"
  }'

# YELLOW: US Login
curl -X POST http://localhost:8000/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "Test123!",
    "timestamp": "2025-10-26T10:30:00Z",
    "device_fingerprint": "us_laptop_002",
    "ip_address": "8.8.8.8",
    "location": "New York, US"
  }'

# RED: Russia Login
curl -X POST http://localhost:8000/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "Test123!",
    "timestamp": "2025-10-26T02:00:00Z",
    "device_fingerprint": "suspicious_device_003",
    "ip_address": "5.188.10.50",
    "location": "Moscow, RU"
  }'
```

---

### Method 2: Using API Documentation (Visual Demo)

1. **Start the backend server**:

   ```bash
   cd backend
   python main.py
   ```

2. **Open the Swagger UI**:

   - Navigate to: http://localhost:8000/docs
   - Click on `POST /api/authenticate`
   - Click "Try it out"

3. **Test each scenario**:
   - Copy/paste the JSON from above
   - Click "Execute"
   - Show the response to your audience

**Advantages**:

- ✅ Visual interface
- ✅ No coding required
- ✅ Professional looking
- ✅ Shows API documentation

---

### Method 3: Using Python Script (Automated Demo)

Create `presentation_demo.py`:

```python
#!/usr/bin/env python3
"""Live demonstration script for presentation"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def demo_scenario(name, payload, expected_risk_level):
    """Demonstrate a login scenario"""
    print("\n" + "="*70)
    print(f"🎯 SCENARIO: {name}")
    print("="*70)
    print(f"\n📍 Location: {payload['location']}")
    print(f"🖥️  IP: {payload['ip_address']}")

    response = requests.post(f"{BASE_URL}/api/authenticate", json=payload)
    result = response.json()

    status = result['status']
    risk = result.get('risk_score', 0) * 100

    # Color code output
    if risk < 30:
        icon = "🟢"
        decision = "ALLOW - Direct Login"
    elif risk < 70:
        icon = "🟡"
        decision = "CAUTION - Require 2FA"
    else:
        icon = "🔴"
        decision = "DANGER - Block/Strong Verification"

    print(f"\n{icon} RISK LEVEL: {risk:.0f}%")
    print(f"📊 STATUS: {status.upper()}")
    print(f"⚖️  DECISION: {decision}")
    print(f"💬 MESSAGE: {result['message']}")

    if status == 'success':
        print("\n✅ User logged in successfully!")
    else:
        print("\n🔐 Additional verification required")

    return result

# Test scenarios
print("="*70)
print("🎓 ZT-VERIFY LIVE DEMONSTRATION")
print("="*70)
print("\nDemonstrating UAE-focused risk-based authentication")
print("Testing 3 scenarios: Green, Yellow, and Red")

# GREEN
demo_scenario(
    "✅ GREEN - UAE Employee",
    {
        "username": "john_doe",
        "password": "Test123!",
        "timestamp": datetime.now().isoformat(),
        "device_fingerprint": "uae_office_laptop_001",
        "ip_address": "5.62.61.123",
        "location": "Dubai, AE"
    },
    "low"
)

# YELLOW
demo_scenario(
    "⚠️  YELLOW - US Business Partner",
    {
        "username": "john_doe",
        "password": "Test123!",
        "timestamp": datetime.now().isoformat(),
        "device_fingerprint": "us_laptop_002",
        "ip_address": "8.8.8.8",
        "location": "New York, US"
    },
    "medium"
)

# RED
demo_scenario(
    "🚨 RED - Russia Suspicious Login",
    {
        "username": "john_doe",
        "password": "Test123!",
        "timestamp": datetime.now().isoformat(),
        "device_fingerprint": "suspicious_device_003",
        "ip_address": "5.188.10.50",
        "location": "Moscow, RU"
    },
    "high"
)

print("\n" + "="*70)
print("✅ DEMONSTRATION COMPLETE")
print("="*70)
print("\nKey Takeaways:")
print("  🟢 UAE logins: Low risk (5-10%) - Direct access")
print("  🟡 US logins: Medium risk (40%) - Require 2FA")
print("  🔴 Russia logins: High risk (80%) - Block/Strong verification")
print("="*70)
```

**Run it**:

```bash
python presentation_demo.py
```

---

## 🌐 Using VPN for Realistic Demo (Advanced)

### Option 1: VPN Testing (Most Realistic)

**Setup**:

1. Install VPN software (NordVPN, ExpressVPN, etc.)
2. Connect to different countries
3. Actually demonstrate the IP/location change

**Demo Flow**:

```
1. Show your local IP → Login from UAE → ✅ Success
2. Connect VPN to US server → Login → ⚠️  2FA Required
3. Connect VPN to Russia → Login → 🚨 High Risk
```

**Pros**:

- 🎯 Most realistic
- 🌍 Shows real geolocation
- 👥 Impressive for audience

**Cons**:

- ⏰ Takes time to switch VPNs
- 💰 Requires VPN subscription
- 🐛 Risk of network issues during demo

---

### Option 2: VM with Network Simulation (Recommended)

**Setup**:

1. Run your Kiosk app in a VM (VirtualBox/VMware)
2. Use the backend API's `location` parameter
3. Simulate different locations without VPN

**Demo Flow**:

```bash
# VM 1: UAE Kiosk
location: "Dubai, AE"
ip: "5.62.61.123"
→ Direct login

# VM 2: US Kiosk
location: "New York, US"
ip: "8.8.8.8"
→ 2FA required

# VM 3: Russia (simulated attack)
location: "Moscow, RU"
ip: "5.188.10.50"
→ Blocked
```

**Pros**:

- ✅ Reliable
- ✅ No network dependencies
- ✅ Can pause/explain between tests

**Cons**:

- 🖥️ Requires VM setup
- 📦 More resources needed

---

### Option 3: Browser Dev Tools (Easiest)

**Setup**:

1. Open browser DevTools (F12)
2. Go to Network tab
3. Modify API requests

**Demo Flow**:

1. Open Kiosk app in browser
2. Intercept login request
3. Modify JSON payload with different locations
4. Show different responses

**Pros**:

- ⚡ Fastest
- 🎯 Shows technical skill
- 💻 No additional setup

**Cons**:

- 🤔 Less visual
- 👥 Audience might not understand

---

## 📝 Recommended Presentation Flow

### 1. Introduction (2 minutes)

"We developed a Zero-Trust authentication system optimized for UAE deployment. Let me show you how it handles different risk levels."

### 2. Demo Setup (1 minute)

- Show the backend running: `python main.py`
- Show the API docs: http://localhost:8000/docs
- Explain the 3 risk levels: Green, Yellow, Red

### 3. Live Demonstrations (5 minutes)

#### Demo 1: 🟢 GREEN - Safe Login

```
"First, a typical employee logging in from Dubai..."
→ Show UAE login
→ Risk: 5%
→ Direct access granted
"As you can see, UAE employees get seamless access"
```

#### Demo 2: 🟡 YELLOW - Caution

```
"Now, a business partner from the US..."
→ Show US login
→ Risk: 40%
→ 2FA required
"The system requires additional verification for foreign locations"
```

#### Demo 3: 🔴 RED - Danger

```
"Finally, a suspicious login from Russia..."
→ Show Russia login
→ Risk: 80%
→ Blocked/Strong verification
"High-risk countries trigger maximum security"
```

### 4. Technical Explanation (3 minutes)

- Show `ml_engine_uae.py` code
- Explain hybrid approach (Rules + ML)
- Show training data (114K samples, AUC 0.9091)
- Mention real attack patterns detected (Romania ASN 3280)

### 5. Q&A

---

## 🎬 Pre-Presentation Checklist

### 1 Day Before:

- [ ] Test all 3 scenarios multiple times
- [ ] Prepare backup demo video (in case of issues)
- [ ] Ensure backend server starts quickly
- [ ] Test on presentation laptop

### 1 Hour Before:

- [ ] Start backend server
- [ ] Verify API responds: `curl http://localhost:8000/api/health`
- [ ] Test one scenario to confirm
- [ ] Have this guide open for reference

### During Presentation:

- [ ] Keep terminal/API docs visible
- [ ] Explain what you're doing before each test
- [ ] Point out the risk scores
- [ ] Highlight the decision (allow/2FA/block)

---

## 🚀 Quick Start Script

Save this as `demo.sh`:

```bash
#!/bin/bash

echo "🚀 Starting ZT-Verify Demo"
echo "=========================="

# Start backend
cd backend
python main.py &
BACKEND_PID=$!

sleep 3

echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""
echo "📖 Open in browser:"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🎯 Run demo:"
echo "   python presentation_demo.py"
echo ""
echo "⏹️  Stop server when done:"
echo "   kill $BACKEND_PID"
```

Run it:

```bash
chmod +x demo.sh
./demo.sh
```

---

## 📊 Expected Results Summary

| Scenario  | Location     | Risk  | Status  | Decision                  |
| --------- | ------------ | ----- | ------- | ------------------------- |
| 🟢 GREEN  | Dubai, AE    | 5-10% | success | Allow direct login        |
| 🟡 YELLOW | New York, US | 40%   | otp     | Require 2FA               |
| 🔴 RED    | Moscow, RU   | 80%   | otp     | Block/Strong verification |

---

## 🎯 Key Points to Emphasize

1. **UAE-Optimized**: System treats UAE as safe baseline
2. **Real ML**: Trained on 114K real login records from Kaggle
3. **Hybrid Approach**: Combines rules (explainable) with ML (accurate)
4. **Fast**: <20ms response time
5. **Practical**: Detects real attack patterns from dataset

---

## 💡 Troubleshooting

### Issue: "Connection refused"

**Solution**: Start backend server

```bash
cd backend && python main.py
```

### Issue: "Invalid credentials"

**Solution**: Use test user from seed_data.py

```
Username: john_doe
Password: Test123!
```

### Issue: Risk score different than expected

**Solution**: Check the `location` format - must be "City, COUNTRY_CODE"

---

## 📦 Files for Presentation

**Demo Script**: `presentation_demo.py` (included above)
**Test Data**: Use JSON examples from this guide
**Backend**: Already integrated with `ml_engine_uae.py`
**Documentation**: `UAE_DEPLOYMENT_SUMMARY.md`

---

## 🎓 Good Luck with Your Presentation!

**Remember**:

- Keep it simple
- Explain as you go
- Highlight the UAE focus
- Show the real dataset/ML training
- Emphasize practical security
