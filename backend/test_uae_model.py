#!/usr/bin/env python3
"""
Test UAE-focused model with realistic UAE deployment scenarios
"""

from ml_engine_uae import predict_risk_hybrid as predict_risk

print("=" * 80)
print("UAE MODEL TESTING - Real Deployment Scenarios")
print("=" * 80)
print()

# Test cases from UAE_TEST_CASES.md
test_cases = [
    ("🟢 GREEN", [
        ("UAE Office - Etisalat", {
            'ip_address': '5.62.61.123',
            'country': 'AE',
            'asn': 5384,
            'device_type': 'desktop',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'browser': 'Chrome 120',
            'os': 'Windows 10',
            'timestamp': '2024-10-25T10:30:00Z'
        }),
        ("UAE Mobile - Du", {
            'ip_address': '213.42.20.55',
            'country': 'AE',
            'asn': 15802,
            'device_type': 'mobile',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
            'browser': 'Safari 17',
            'os': 'iOS 17',
            'timestamp': '2024-10-25T06:00:00Z'
        }),
        ("Dubai Internet City", {
            'ip_address': '185.60.218.45',
            'country': 'AE',
            'asn': 42298,
            'device_type': 'desktop',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'browser': 'Chrome 119',
            'os': 'Mac OS X 10.15',
            'timestamp': '2024-10-25T08:00:00Z'
        }),
        ("Saudi Arabia (Neighbor)", {
            'ip_address': '188.245.35.10',
            'country': 'SA',
            'asn': 25019,
            'device_type': 'mobile',
            'user_agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
            'browser': 'Chrome 118',
            'os': 'Android 13',
            'timestamp': '2024-10-25T07:00:00Z'
        }),
    ]),
    
    ("🟡 YELLOW", [
        ("Late Night UAE (3 AM)", {
            'ip_address': '5.62.61.200',
            'country': 'AE',
            'asn': 5384,
            'device_type': 'desktop',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'browser': 'Chrome 120',
            'os': 'Windows 10',
            'timestamp': '2024-10-25T23:00:00Z'
        }),
        ("India (Outsourcing)", {
            'ip_address': '103.21.124.88',
            'country': 'IN',
            'asn': 9829,
            'device_type': 'desktop',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'browser': 'Chrome 118',
            'os': 'Windows 10',
            'timestamp': '2024-10-25T08:30:00Z'
        }),
        ("Pakistan", {
            'ip_address': '39.42.100.50',
            'country': 'PK',
            'asn': 45595,
            'device_type': 'mobile',
            'user_agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36',
            'browser': 'Chrome 115',
            'os': 'Android 12',
            'timestamp': '2024-10-25T06:00:00Z'
        }),
        ("AWS Singapore (VPN)", {
            'ip_address': '3.25.45.100',
            'country': 'SG',
            'asn': 16509,
            'device_type': 'desktop',
            'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'browser': 'Chrome 119',
            'os': 'Linux',
            'timestamp': '2024-10-25T07:00:00Z'
        }),
    ]),
    
    ("🔴 RED", [
        ("Russia", {
            'ip_address': '5.188.10.50',
            'country': 'RU',
            'asn': 200350,
            'device_type': 'desktop',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'browser': 'Chrome 118',
            'os': 'Windows 10',
            'timestamp': '2024-10-25T08:00:00Z'
        }),
        ("China", {
            'ip_address': '111.206.65.33',
            'country': 'CN',
            'asn': 4134,
            'device_type': 'desktop',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'browser': 'Chrome 117',
            'os': 'Windows 10',
            'timestamp': '2024-10-25T05:00:00Z'
        }),
        ("Nigeria (High Fraud)", {
            'ip_address': '105.112.0.50',
            'country': 'NG',
            'asn': 37148,
            'device_type': 'mobile',
            'user_agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
            'browser': 'Chrome 114',
            'os': 'Android 10',
            'timestamp': '2024-10-25T10:00:00Z'
        }),
        ("Python Bot", {
            'ip_address': '5.62.61.180',
            'country': 'AE',
            'asn': 5384,
            'device_type': 'desktop',
            'user_agent': 'Python-urllib/3.8',
            'browser': 'Python',
            'os': 'Linux',
            'timestamp': '2024-10-25T02:00:00Z'
        }),
        ("Romania Attack (from dataset)", {
            'ip_address': '10.4.1.162',
            'country': 'RO',
            'asn': 3280,
            'device_type': 'desktop',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36',
            'browser': 'Chrome 91',
            'os': 'Mac OS X 10.14',
            'timestamp': '2024-10-25T02:00:00Z'
        }),
        ("Tor Exit Node", {
            'ip_address': '185.220.101.1',
            'country': 'NL',
            'asn': 206264,
            'device_type': 'desktop',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
            'browser': 'Firefox 102',
            'os': 'Windows 10',
            'timestamp': '2024-10-25T12:00:00Z'
        }),
    ]),
]

for category, tests in test_cases:
    print(f"\n{'='*80}")
    print(f"{category} CASES (Expected Risk Level)")
    print("="*80)
    
    for name, data in tests:
        result = predict_risk('testuser', data)
        risk = result['risk_score']
        level = result['risk_level']
        is_anomaly = result['is_anomaly']
        
        # Color code the output
        if risk < 30:
            symbol = "✅"
            color_level = "LOW"
        elif risk < 70:
            symbol = "⚠️ "
            color_level = "MEDIUM"
        else:
            symbol = "🚨"
            color_level = "HIGH"
        
        print(f"\n{symbol} {name}")
        print(f"   Risk Score: {risk}/100")
        print(f"   Risk Level: {color_level} ({level})")
        print(f"   Is Anomaly: {'YES' if is_anomaly else 'NO'}")
        if 'risk_factors' in result:
            print(f"   Reasons:")
            for factor in result['risk_factors']:
                print(f"      {factor}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
Expected Behavior:
  🟢 GREEN  (0-30%):   Allow without extra verification
  🟡 YELLOW (30-70%):  Require 2FA or email verification
  🔴 RED    (70-100%): Block or require strong verification

The model should:
  ✓ Allow UAE and Gulf countries with low risk
  ⚠️  Flag regional countries and unusual patterns as medium risk
  🚨 Block high-risk countries and attack patterns
""")
print("="*80)
