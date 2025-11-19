#!/usr/bin/env python3
"""
Test ML risk assessment API
Tests various login scenarios to check risk score distribution
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://wallpaper-pregnant-onion-supposed.trycloudflare.com/api"

# Test scenarios with different risk profiles
TEST_SCENARIOS = [
    {
        "name": "UAE Local - Low Risk",
        "username": "test_user_uae",
        "password": "Test123!",
        "ip_address": "185.94.0.50",  # UAE IP
        "location": "Dubai, AE",
        "expected_risk": "LOW"
    },
    {
        "name": "Foreign IP - Medium Risk",
        "username": "test_user_foreign",
        "password": "Test123!",
        "ip_address": "203.0.113.50",  # Generic foreign IP
        "location": "London, GB",
        "expected_risk": "MEDIUM"
    },
    {
        "name": "Suspicious Country - High Risk",
        "username": "test_user_suspicious",
        "password": "Test123!",
        "ip_address": "198.51.100.50",  # Suspicious IP
        "location": "Moscow, RU",
        "expected_risk": "HIGH"
    },
    {
        "name": "Hardcoded Green User",
        "username": "green_user",
        "password": "Test123!",
        "ip_address": "192.168.1.100",
        "location": "Dubai, AE",
        "expected_risk": "LOW (hardcoded 15)"
    },
    {
        "name": "Hardcoded Yellow User",
        "username": "yellow_user",
        "password": "Test123!",
        "ip_address": "192.168.1.100",
        "location": "Dubai, AE",
        "expected_risk": "MEDIUM (hardcoded 50)"
    },
    {
        "name": "Hardcoded Red User",
        "username": "red_user",
        "password": "Test123!",
        "ip_address": "192.168.1.100",
        "location": "Dubai, AE",
        "expected_risk": "HIGH (hardcoded 85)"
    }
]

def get_risk_level(score):
    """Convert risk score to level"""
    if score < 30:
        return "🟢 LOW"
    elif score < 70:
        return "🟡 MEDIUM"
    else:
        return "🔴 HIGH"

def test_authentication(scenario):
    """Test authentication endpoint with scenario"""
    print(f"\n{'='*70}")
    print(f"Testing: {scenario['name']}")
    print(f"Expected: {scenario['expected_risk']}")
    print(f"{'='*70}")
    
    auth_data = {
        "username": scenario["username"],
        "password": scenario["password"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "device_fingerprint": "test_device_12345",
        "ip_address": scenario["ip_address"],
        "location": scenario["location"]
    }
    
    print(f"Request Data:")
    print(f"  Username: {auth_data['username']}")
    print(f"  IP: {auth_data['ip_address']}")
    print(f"  Location: {auth_data['location']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/authenticate",
            json=auth_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            risk_score_raw = result.get('risk_score')
            
            if risk_score_raw is not None:
                risk_score = risk_score_raw * 100  # Convert to 0-100
                risk_level = get_risk_level(risk_score)
                
                print(f"\n✓ Response received")
                print(f"  Status: {result.get('status')}")
                print(f"  Risk Score: {risk_score:.1f}/100")
                print(f"  Risk Level: {risk_level}")
                
                # Check if it matches expected
                if "LOW" in scenario['expected_risk'] and risk_score < 30:
                    print(f"  ✓ Matches expected LOW risk")
                elif "MEDIUM" in scenario['expected_risk'] and 30 <= risk_score < 70:
                    print(f"  ✓ Matches expected MEDIUM risk")
                elif "HIGH" in scenario['expected_risk'] and risk_score >= 70:
                    print(f"  ✓ Matches expected HIGH risk")
                else:
                    print(f"  ⚠ Risk level different from expected!")
                
                return risk_score
            else:
                print(f"  ✗ No risk score returned")
                print(f"  Status: {result.get('status')}")
                print(f"  Message: {result.get('message')}")
                return None
        else:
            print(f"  ✗ Request failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Connection error: {str(e)}")
        return None

def main():
    print("="*70)
    print("ML RISK ASSESSMENT API TEST")
    print("="*70)
    print(f"Backend URL: {BASE_URL}")
    print(f"Testing {len(TEST_SCENARIOS)} scenarios...")
    
    results = []
    
    for scenario in TEST_SCENARIOS:
        score = test_authentication(scenario)
        if score is not None:
            results.append({
                'name': scenario['name'],
                'score': score,
                'level': get_risk_level(score)
            })
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if results:
        low_count = sum(1 for r in results if r['score'] < 30)
        medium_count = sum(1 for r in results if 30 <= r['score'] < 70)
        high_count = sum(1 for r in results if r['score'] >= 70)
        
        print(f"\nRisk Distribution:")
        print(f"  🟢 LOW (0-29):      {low_count} tests")
        print(f"  🟡 MEDIUM (30-69):   {medium_count} tests")
        print(f"  🔴 HIGH (70-100):    {high_count} tests")
        
        print(f"\nDetailed Results:")
        for r in results:
            print(f"  {r['level']}: {r['name']} ({r['score']:.1f})")
        
        if medium_count > high_count + low_count:
            print(f"\n⚠ WARNING: High number of MEDIUM risk cases detected!")
            print(f"   This might indicate ML model defaults or issues.")
    else:
        print("No successful tests completed")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
