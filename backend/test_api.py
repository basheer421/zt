#!/usr/bin/env python3
"""
Test script for ZT-Verify API endpoints
Tests the authentication and health check endpoints
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✓ Health check passed!")

def test_authenticate_invalid_user():
    """Test authentication with invalid username"""
    print("\n" + "=" * 60)
    print("TEST 2: Authenticate - Invalid User")
    print("=" * 60)
    
    payload = {
        "username": "nonexistent_user",
        "password": "SomePassword123!",
        "timestamp": datetime.now().isoformat(),
        "device_fingerprint": "test_device_001",
        "ip_address": "192.168.1.100",
        "location": "New York, US"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/authenticate", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "invalid_credentials"
    print("✓ Invalid user test passed!")

def test_authenticate_valid_user():
    """Test authentication with valid credentials"""
    print("\n" + "=" * 60)
    print("TEST 3: Authenticate - Valid User (john_doe)")
    print("=" * 60)
    print("Note: Using test user 'john_doe' with password 'Test123!' from seed_data.py")
    print("Note: US location triggers medium risk (40%) in UAE-focused model")
    
    payload = {
        "username": "john_doe",
        "password": "Test123!",
        "timestamp": datetime.now().isoformat(),
        "device_fingerprint": "test_device_002",
        "ip_address": "192.168.1.101",
        "location": "San Francisco, US"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/authenticate", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    # UAE model triggers 2FA for US logins (medium risk)
    assert response.json()["status"] in ["success", "otp"]
    assert response.json()["username"] == "john_doe"
    print(f"✓ Valid user authentication passed! (Status: {response.json()['status']})")

def test_authenticate_wrong_password():
    """Test authentication with wrong password"""
    print("\n" + "=" * 60)
    print("TEST 4: Authenticate - Wrong Password")
    print("=" * 60)
    
    payload = {
        "username": "john_doe",
        "password": "WrongPassword123!",
        "timestamp": datetime.now().isoformat(),
        "device_fingerprint": "test_device_003",
        "ip_address": "192.168.1.102",
        "location": "Boston, US"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/authenticate", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "invalid_credentials"
    print("✓ Wrong password test passed!")

def test_known_device():
    """Test authentication with a known device (lower risk score)"""
    print("\n" + "=" * 60)
    print("TEST 5: Authenticate - Known Device")
    print("=" * 60)
    print("Authenticating with same device twice to test device trust")
    
    payload = {
        "username": "john_doe",
        "password": "SecurePass123!",
        "timestamp": datetime.now().isoformat(),
        "device_fingerprint": "known_device_123",
        "ip_address": "192.168.1.103",
        "location": "Seattle, US"
    }
    
    # First login - device will be registered
    print("\nFirst login (new device):")
    response1 = requests.post(f"{BASE_URL}/api/authenticate", json=payload)
    print(f"Response: {json.dumps(response1.json(), indent=2)}")
    risk_score_1 = response1.json().get("risk_score", 0)
    
    # Second login - device is now known
    print("\nSecond login (known device):")
    response2 = requests.post(f"{BASE_URL}/api/authenticate", json=payload)
    print(f"Response: {json.dumps(response2.json(), indent=2)}")
    risk_score_2 = response2.json().get("risk_score", 0)
    
    print(f"\nRisk Score Comparison:")
    print(f"  First login (new device): {risk_score_1}")
    print(f"  Second login (known device): {risk_score_2}")
    
    assert risk_score_2 < risk_score_1, "Known device should have lower risk score"
    print("✓ Known device test passed!")

def test_authenticate_uae_user():
    """Test authentication from UAE (should be low risk)"""
    print("\n" + "=" * 60)
    print("TEST 5: Authenticate - UAE User (Low Risk)")
    print("=" * 60)
    print("Note: UAE location should trigger low risk (5-10%) and allow direct login")
    
    payload = {
        "username": "john_doe",
        "password": "Test123!",
        "timestamp": datetime.now().isoformat(),
        "device_fingerprint": "test_device_uae",
        "ip_address": "5.62.61.123",  # UAE Etisalat IP
        "location": "Dubai, AE"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/authenticate", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    # UAE location should allow direct login (low risk)
    assert response.json()["status"] == "success"
    assert response.json()["username"] == "john_doe"
    risk = response.json().get("risk_score", 0)
    print(f"✓ UAE authentication passed! (Risk: {risk*100:.0f}%)")

def test_authenticate_high_risk():
    """Test authentication from high-risk country"""
    print("\n" + "=" * 60)
    print("TEST 6: Authenticate - High Risk Country (Russia)")
    print("=" * 60)
    print("Note: Russia should trigger high risk (80%) and require 2FA")
    
    payload = {
        "username": "john_doe",
        "password": "Test123!",
        "timestamp": datetime.now().isoformat(),
        "device_fingerprint": "test_device_russia",
        "ip_address": "5.188.10.50",
        "location": "Moscow, RU"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/authenticate", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    # Russia should require 2FA (high risk)
    assert response.json()["status"] == "otp"
    assert response.json()["username"] == "john_doe"
    risk = response.json().get("risk_score", 0)
    print(f"✓ High-risk authentication correctly requires 2FA! (Risk: {risk*100:.0f}%)")

def test_api_docs():
    """Test API documentation endpoint"""
    print("\n" + "=" * 60)
    print("TEST 7: API Documentation")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/docs")
    print(f"Status Code: {response.status_code}")
    
    assert response.status_code == 200
    print("✓ API documentation accessible!")

if __name__ == "__main__":
    print("=" * 60)
    print("ZT-VERIFY API TEST SUITE")
    print("=" * 60)
    print("Make sure the API server is running on http://localhost:8000")
    print("Run: python3 main.py")
    print("=" * 60)
    
    try:
        test_health_check()
        test_authenticate_invalid_user()
        test_authenticate_valid_user()
        test_authenticate_wrong_password()
        test_authenticate_uae_user()
        test_authenticate_high_risk()
        test_api_docs()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print(f"\nAPI Documentation: {BASE_URL}/docs")
        print(f"Interactive API: {BASE_URL}/docs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the server is running: python3 main.py")
        exit(1)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        exit(1)
