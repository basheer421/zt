#!/usr/bin/env python3
"""
Live demonstration script for university presentation
Shows 3 risk levels: Green (UAE), Yellow (US), Red (Russia)
"""

import requests
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000"

def check_server():
    """Check if backend server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def demo_scenario(name, emoji, payload, expected_risk_level):
    """Demonstrate a login scenario with visual output"""
    print("\n" + "="*80)
    print(f"{emoji} SCENARIO: {name}")
    print("="*80)
    print(f"\n📍 Location: {payload['location']}")
    print(f"🖥️  IP Address: {payload['ip_address']}")
    print(f"👤 Username: {payload['username']}")
    print(f"🔑 Device: {payload['device_fingerprint']}")
    
    # Make request
    try:
        response = requests.post(f"{BASE_URL}/api/authenticate", json=payload, timeout=5)
        result = response.json()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None
    
    status = result.get('status', 'unknown')
    risk = result.get('risk_score', 0) * 100
    message = result.get('message', '')
    
    # Determine risk level and decision
    if risk < 30:
        icon = "🟢"
        risk_label = "LOW RISK"
        decision = "✅ ALLOW - Direct Login"
        color = "\033[92m"  # Green
    elif risk < 70:
        icon = "🟡"
        risk_label = "MEDIUM RISK"
        decision = "⚠️  CAUTION - Require 2FA"
        color = "\033[93m"  # Yellow
    else:
        icon = "🔴"
        risk_label = "HIGH RISK"
        decision = "🚨 DANGER - Block/Strong Verification"
        color = "\033[91m"  # Red
    
    reset = "\033[0m"
    
    # Display results
    print(f"\n{icon} {color}RISK LEVEL: {risk:.0f}% ({risk_label}){reset}")
    print(f"📊 STATUS: {status.upper()}")
    print(f"⚖️  DECISION: {decision}")
    print(f"💬 MESSAGE: {message}")
    
    # Show what happens next
    if status == 'success':
        print(f"\n{color}✅ Result: User logged in successfully!{reset}")
        print("   → Access granted to system")
        print("   → No additional verification needed")
    elif status == 'otp':
        print(f"\n{color}🔐 Result: Additional verification required{reset}")
        print("   → 2FA code sent to user")
        print("   → Must verify before access granted")
    else:
        print(f"\n{color}❌ Result: Access denied{reset}")
    
    print("\n" + "-"*80)
    
    return result

def main():
    """Run the demonstration"""
    print("="*80)
    print("🎓 ZT-VERIFY LIVE DEMONSTRATION")
    print("="*80)
    print("\n🌍 UAE-Focused Risk-Based Authentication System")
    print("📊 Testing 3 Risk Levels: Green, Yellow, and Red")
    print("🤖 Powered by Hybrid ML + Rules Engine")
    print("\n" + "="*80)
    
    # Check if server is running
    if not check_server():
        print("\n❌ ERROR: Backend server is not running!")
        print("\n💡 Start the server first:")
        print("   cd backend")
        print("   python main.py")
        print("\nThen run this demo again.")
        sys.exit(1)
    
    print("\n✅ Backend server is online")
    print("🔗 API URL: " + BASE_URL)
    
    input("\n⏸️  Press Enter to start the demonstration...")
    
    # ========================================================================
    # SCENARIO 1: GREEN - UAE Employee
    # ========================================================================
    result1 = demo_scenario(
        "✅ GREEN - UAE Employee Login",
        "🟢",
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
    
    print("\n📝 Explanation:")
    print("   • Country: UAE (AE) - Safe baseline")
    print("   • IP: 5.62.61.123 (UAE Etisalat)")
    print("   • Time: Business hours")
    print("   • Decision: Low risk → Allow direct access")
    
    input("\n⏸️  Press Enter for next scenario...")
    
    # ========================================================================
    # SCENARIO 2: YELLOW - US Business Partner
    # ========================================================================
    result2 = demo_scenario(
        "⚠️  YELLOW - US Business Partner Login",
        "🟡",
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
    
    print("\n📝 Explanation:")
    print("   • Country: United States - Acceptable but not UAE")
    print("   • IP: 8.8.8.8 (Google DNS)")
    print("   • Device: Unknown device from foreign location")
    print("   • Decision: Medium risk → Require 2FA")
    
    input("\n⏸️  Press Enter for final scenario...")
    
    # ========================================================================
    # SCENARIO 3: RED - Russia Suspicious Login
    # ========================================================================
    result3 = demo_scenario(
        "🚨 RED - Russia Suspicious Login Attempt",
        "🔴",
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
    
    print("\n📝 Explanation:")
    print("   • Country: Russia (RU) - High-risk country")
    print("   • IP: 5.188.10.50 (Russian ISP)")
    print("   • Device: Unknown suspicious device")
    print("   • Decision: High risk → Block or strong verification")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*80)
    
    print("\n📊 Results Summary:")
    print("┌─────────────────────────────┬──────────┬────────────┬─────────────────┐")
    print("│ Scenario                    │ Location │ Risk Score │ Decision        │")
    print("├─────────────────────────────┼──────────┼────────────┼─────────────────┤")
    
    if result1:
        print(f"│ 🟢 UAE Employee             │ Dubai    │ {result1.get('risk_score', 0)*100:>5.0f}%    │ ✅ Allow        │")
    if result2:
        print(f"│ 🟡 US Business Partner      │ New York │ {result2.get('risk_score', 0)*100:>5.0f}%    │ ⚠️  2FA Required │")
    if result3:
        print(f"│ 🔴 Russia Suspicious        │ Moscow   │ {result3.get('risk_score', 0)*100:>5.0f}%    │ 🚨 Block        │")
    
    print("└─────────────────────────────┴──────────┴────────────┴─────────────────┘")
    
    print("\n🎯 Key Takeaways:")
    print("   1. 🟢 UAE logins: Low risk (5-10%) → Seamless access")
    print("   2. 🟡 Foreign acceptable countries: Medium risk (40%) → Extra verification")
    print("   3. 🔴 High-risk countries: High risk (70-100%) → Strong security measures")
    
    print("\n🤖 Technology Stack:")
    print("   • Hybrid ML + Rules approach")
    print("   • Trained on 114,561 real login records from Kaggle RBA dataset")
    print("   • AUC Score: 0.9091 (excellent discrimination)")
    print("   • Fast inference: <20ms per prediction")
    
    print("\n🌍 UAE Optimization:")
    print("   • Treats UAE and Gulf countries as safe baseline")
    print("   • Recognizes local ISPs (Etisalat, Du)")
    print("   • Detects real attack patterns from dataset")
    
    print("\n" + "="*80)
    print("💡 For more details, see:")
    print("   • UAE_DEPLOYMENT_SUMMARY.md")
    print("   • UAE_TEST_CASES.md")
    print("   • API Documentation: http://localhost:8000/docs")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
