# 🎯 Quick Start - Presentation Demo

## 🚀 Start the Demo (One Command)

```bash
cd backend
./start_demo.sh
```

Then run the automated demo:

```bash
python presentation_demo.py
```

That's it! 🎉

---

## 📊 What You'll See

### 🟢 Scenario 1: UAE Employee
- **Location**: Dubai, AE
- **Risk**: 10% (LOW)
- **Result**: ✅ Direct login allowed

### 🟡 Scenario 2: US Business Partner
- **Location**: New York, US
- **Risk**: 40% (MEDIUM)
- **Result**: ⚠️  2FA required

### 🔴 Scenario 3: Russia Suspicious
- **Location**: Moscow, RU
- **Risk**: 80% (HIGH)
- **Result**: 🚨 Blocked/Strong verification

---

## 📁 All Demo Files

| File | Purpose |
|------|---------|
| `PRESENTATION_TESTING_GUIDE.md` | Complete testing guide with all options |
| `presentation_demo.py` | Automated demo script (recommended) |
| `test_scenarios.json` | All test cases in JSON format |
| `start_demo.sh` | One-command server startup |
| `UAE_DEPLOYMENT_SUMMARY.md` | Technical documentation |
| `UAE_TEST_CASES.md` | 20 detailed test cases |

---

## 🎬 Alternative Demo Methods

### Option 1: Swagger UI (Visual)
1. Start server: `python main.py`
2. Open: http://localhost:8000/docs
3. Click "POST /api/authenticate"
4. Use test cases from `test_scenarios.json`

### Option 2: curl (Command Line)
```bash
# GREEN
curl -X POST http://localhost:8000/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"Test123!","timestamp":"2025-10-26T10:30:00Z","device_fingerprint":"uae_office_laptop_001","ip_address":"5.62.61.123","location":"Dubai, AE"}'

# YELLOW  
curl -X POST http://localhost:8000/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"Test123!","timestamp":"2025-10-26T10:30:00Z","device_fingerprint":"us_laptop_002","ip_address":"8.8.8.8","location":"New York, US"}'

# RED
curl -X POST http://localhost:8000/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"Test123!","timestamp":"2025-10-26T02:00:00Z","device_fingerprint":"suspicious_device_003","ip_address":"5.188.10.50","location":"Moscow, RU"}'
```

---

## 🛑 Stop the Server

```bash
pkill -f 'python.*main.py'
```

Or use the PID shown when you started:
```bash
kill <PID>
```

---

## ✅ Pre-Presentation Checklist

- [ ] Test demo script runs successfully
- [ ] All 3 scenarios show correct risk levels
- [ ] Backend responds quickly (<1 second)
- [ ] Have backup if network fails (screenshots/video)
- [ ] Know your talking points (see PRESENTATION_TESTING_GUIDE.md)

---

## 🎓 Key Points to Mention

1. **UAE-Optimized**: Treats UAE as safe baseline
2. **Real Data**: Trained on 114K real login records
3. **Hybrid Approach**: ML + Rules for explainability
4. **Fast**: <20ms response time
5. **Practical**: Detects real attack patterns

Good luck! 🚀
