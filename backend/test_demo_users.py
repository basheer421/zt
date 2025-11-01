#!/usr/bin/env python3
"""
Test the hardcoded demo users
Verifies that green_user, yellow_user, and red_user return correct risk scores
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test data for each user
TEST_USERS = [
    {
        'username': 'green_user',
        'expected_risk': 15,
        'expected_level': 'low',
        'color': '🟢 GREEN'
    },
    {
        'username': 'yellow_user',
        'expected_risk': 50,
        'expected_level': 'medium',
        'color': '🟡 YELLOW'
    },
    {
        'username': 'red_user',
        'expected_risk': 85,
        'expected_level': 'high',
        'color': '🔴 RED'
    }
]

def test_demo_users():
    """Test all demo users"""
    print("=" * 60)
    print("TESTING HARDCODED DEMO USERS")
    print("=" * 60)
    print()
    
    for user in TEST_USERS:
        print(f"Testing {user['username']} ({user['color']})...")
        
        # Prepare authentication request
        auth_data = {
            "username": user['username'],
            "password": "Test123!",
            "timestamp": "2025-11-01T10:00:00Z",
            "device_fingerprint": "test_device_12345",
            "ip_address": "192.168.1.100",
            "location": "Dubai, AE"
        }
        
        try:
            # Send authentication request
            response = requests.post(
                f"{BASE_URL}/api/authenticate",
                json=auth_data
            )
            
            if response.status_code == 200:
                result = response.json()
                risk_score_raw = result.get('risk_score')
                
                print(f"  ✓ Response received")
                print(f"  Status: {result.get('status')}")
                
                if risk_score_raw is not None:
                    risk_score = risk_score_raw * 100  # Convert back to 0-100
                    print(f"  Risk Score: {risk_score:.0f}/100")
                    print(f"  Expected: {user['expected_risk']}/100")
                    
                    # Verify risk score matches expected
                    if abs(risk_score - user['expected_risk']) < 1:
                        print(f"  ✓ Risk score matches expected value!")
                    else:
                        print(f"  ✗ Risk score mismatch! Got {risk_score}, expected {user['expected_risk']}")
                else:
                    print(f"  ✗ No risk score returned (user might need to be created first)")
                
                print()
            else:
                print(f"  ✗ Request failed with status {response.status_code}")
                print(f"  Response: {response.text}")
                print()
        
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Cannot connect to {BASE_URL}")
            print(f"  Make sure the backend is running!")
            print()
            break
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            print()
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_demo_users()
