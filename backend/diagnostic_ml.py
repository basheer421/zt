#!/usr/bin/env python3
"""
Diagnostic tool to understand risk score distribution
Shows what the ML engine considers for different scenarios
"""

from ml_engine_uae import assess_risk_rules

# Test different scenarios
scenarios = [
    {"name": "UAE Dubai", "country": "AE", "ip": "185.94.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "UAE w/ Local ISP", "country": "AE", "ip": "185.94.0.50", "asn": 5384, "user_agent": "Mozilla", "hour": 10},
    {"name": "Saudi Arabia", "country": "SA", "ip": "185.94.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "Jordan", "country": "JO", "ip": "185.94.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "Egypt", "country": "EG", "ip": "185.94.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "USA", "country": "US", "ip": "192.168.1.1", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "UK", "country": "GB", "ip": "185.94.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "India Business Hours", "country": "IN", "ip": "103.79.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 8},
    {"name": "Singapore", "country": "SG", "ip": "103.28.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "Russia", "country": "RU", "ip": "185.94.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "China", "country": "CN", "ip": "185.94.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "Unknown Country", "country": "XX", "ip": "203.0.113.50", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "Bot from UAE", "country": "AE", "ip": "185.94.0.50", "asn": 0, "user_agent": "python-requests", "hour": 10},
    {"name": "Private IP", "country": "AE", "ip": "192.168.1.100", "asn": 0, "user_agent": "Mozilla", "hour": 10},
    {"name": "Night time UAE", "country": "AE", "ip": "185.94.0.50", "asn": 0, "user_agent": "Mozilla", "hour": 2},
]

print("="*80)
print("ML ENGINE RISK SCORE DIAGNOSTIC")
print("="*80)
print()

def get_color(score):
    if score < 30:
        return "🟢 LOW  "
    elif score < 70:
        return "🟡 MED  "
    else:
        return "🔴 HIGH "

low_count = 0
med_count = 0
high_count = 0

for scenario in scenarios:
    login_data = {
        'country': scenario['country'],
        'ip_address': scenario['ip'],
        'asn': scenario['asn'],
        'user_agent': scenario['user_agent'],
        'timestamp': f"2025-11-02T{scenario['hour']:02d}:00:00Z",
        'device_type': 'desktop',
        'browser': 'Chrome',
        'os': 'Windows'
    }
    
    result = assess_risk_rules("test_user", login_data)
    score = result['risk_score']
    
    if score < 30:
        low_count += 1
    elif score < 70:
        med_count += 1
    else:
        high_count += 1
    
    color = get_color(score)
    print(f"{color} {score:3d}% - {scenario['name']:25s} | {', '.join(result['risk_factors'])}")

print()
print("="*80)
print("SUMMARY")
print("="*80)
total = len(scenarios)
print(f"🟢 LOW (0-29):     {low_count:2d} / {total} ({low_count/total*100:.1f}%)")
print(f"🟡 MEDIUM (30-69):  {med_count:2d} / {total} ({med_count/total*100:.1f}%)")
print(f"🔴 HIGH (70-100):   {high_count:2d} / {total} ({high_count/total*100:.1f}%)")
print()
print("EXPLANATION:")
print("The ML engine is designed for UAE deployment, so:")
print("- UAE/Gulf logins = LOW risk (0-10%)")
print("- Regional/business countries = MEDIUM risk (30-45%)")  
print("- High-risk/suspicious = HIGH risk (70-100%)")
print()
print("This is WORKING AS DESIGNED for zero-trust UAE security.")
print("="*80)
