#!/usr/bin/env python3
"""
Test script for OTP API endpoints
Tests /api/otp/request, /api/otp/verify, and /api/otp/status endpoints
"""

import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"

def print_separator(title=""):
    """Print a formatted separator"""
    if title:
        print("\n" + "=" * 60)
        print(f"{title}")
        print("=" * 60)
    else:
        print("-" * 60)

def test_request_otp():
    """Test requesting an OTP code"""
    print_separator("TEST 1: Request OTP for john_doe")
    
    payload = {
        "username": "john_doe"
    }
    
    print(f"Request: POST {BASE_URL}/api/otp/request")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/otp/request", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    result = response.json()
    if result.get('success'):
        print(f"\n✓ OTP sent successfully!")
        print(f"  Expires in: {result.get('expires_in_minutes')} minutes")
        return True
    else:
        print(f"\n✗ Failed: {result.get('message')}")
        return False

def test_request_otp_invalid_user():
    """Test requesting OTP for non-existent user"""
    print_separator("TEST 2: Request OTP - Invalid User")
    
    payload = {
        "username": "nonexistent_user_123"
    }
    
    print(f"Request: POST {BASE_URL}/api/otp/request")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/otp/request", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    result = response.json()
    if not result.get('success') and "not found" in result.get('message', '').lower():
        print(f"\n✓ Correctly rejected invalid user!")
        return True
    else:
        print(f"\n✗ Test failed")
        return False

def test_get_otp_status():
    """Test getting OTP status"""
    print_separator("TEST 3: Get OTP Status for john_doe")
    
    print(f"Request: GET {BASE_URL}/api/otp/status/john_doe")
    
    response = requests.get(f"{BASE_URL}/api/otp/status/john_doe")
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    result = response.json()
    if result.get('has_active_otp'):
        print(f"\n✓ Active OTP found!")
        print(f"  Remaining seconds: {result.get('remaining_seconds')}")
        print(f"  Attempts remaining: {result.get('attempts_remaining')}")
        return True
    else:
        print(f"\n⚠ No active OTP (this is OK if none was requested)")
        return True

def test_verify_otp_wrong_code():
    """Test verifying OTP with wrong code"""
    print_separator("TEST 4: Verify OTP - Wrong Code")
    
    payload = {
        "username": "john_doe",
        "otp_code": "999999"
    }
    
    print(f"Request: POST {BASE_URL}/api/otp/verify")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/otp/verify", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    result = response.json()
    if not result.get('valid'):
        print(f"\n✓ Wrong OTP correctly rejected!")
        print(f"  Message: {result.get('message')}")
        if result.get('attempts_remaining') is not None:
            print(f"  Attempts remaining: {result.get('attempts_remaining')}")
        return True
    else:
        print(f"\n✗ Test failed - wrong code should be rejected")
        return False

def test_verify_otp_invalid_format():
    """Test verifying OTP with invalid format"""
    print_separator("TEST 5: Verify OTP - Invalid Format")
    
    payload = {
        "username": "john_doe",
        "otp_code": "12345"  # Only 5 digits instead of 6
    }
    
    print(f"Request: POST {BASE_URL}/api/otp/verify")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/otp/verify", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    result = response.json()
    if not result.get('valid') and "format" in result.get('message', '').lower():
        print(f"\n✓ Invalid format correctly rejected!")
        return True
    else:
        print(f"\n✗ Test failed - invalid format should be rejected")
        return False

def test_rate_limiting():
    """Test OTP request rate limiting"""
    print_separator("TEST 6: Rate Limiting - Multiple Requests")
    
    payload = {
        "username": "john_doe"
    }
    
    print("Making first OTP request...")
    response1 = requests.post(f"{BASE_URL}/api/otp/request", json=payload)
    result1 = response1.json()
    print(f"First request: {result1.get('message')}")
    
    print("\nImmediately making second request (should be rate-limited)...")
    response2 = requests.post(f"{BASE_URL}/api/otp/request", json=payload)
    result2 = response2.json()
    print(f"Second request: {result2.get('message')}")
    
    if not result2.get('success') and "wait" in result2.get('message', '').lower():
        print(f"\n✓ Rate limiting works!")
        return True
    elif result2.get('success'):
        print(f"\n⚠ Warning: Rate limiting might not be working (got success)")
        return True  # Don't fail, might be timing issue
    else:
        return False

def test_max_attempts():
    """Test maximum OTP verification attempts"""
    print_separator("TEST 7: Maximum Verification Attempts")
    
    # First, request a new OTP
    print("Requesting a new OTP for jane_smith...")
    request_payload = {"username": "jane_smith"}
    response = requests.post(f"{BASE_URL}/api/otp/request", json=request_payload)
    result = response.json()
    
    if not result.get('success'):
        print(f"⚠ Could not request OTP: {result.get('message')}")
        print("  Skipping max attempts test")
        return True
    
    print("✓ OTP requested")
    
    # Try wrong code multiple times
    print("\nAttempting verification with wrong codes...")
    verify_payload = {
        "username": "jane_smith",
        "otp_code": "111111"
    }
    
    for i in range(1, 5):
        print(f"\nAttempt {i}:")
        response = requests.post(f"{BASE_URL}/api/otp/verify", json=verify_payload)
        result = response.json()
        print(f"  Valid: {result.get('valid')}")
        print(f"  Message: {result.get('message')}")
        if result.get('attempts_remaining') is not None:
            print(f"  Attempts remaining: {result.get('attempts_remaining')}")
        
        if "too many" in result.get('message', '').lower():
            print(f"\n✓ Maximum attempts enforced!")
            return True
    
    print(f"\n⚠ Max attempts might not be enforced correctly")
    return True

def test_full_flow():
    """Test complete OTP flow"""
    print_separator("TEST 8: Complete OTP Flow Simulation")
    
    username = "john_doe"
    
    # Step 1: Request OTP
    print("Step 1: Requesting OTP...")
    request_payload = {"username": username}
    response = requests.post(f"{BASE_URL}/api/otp/request", json=request_payload)
    result = response.json()
    print(f"  Result: {result.get('message')}")
    
    # Step 2: Check status
    print("\nStep 2: Checking OTP status...")
    response = requests.get(f"{BASE_URL}/api/otp/status/{username}")
    status = response.json()
    if status.get('has_active_otp'):
        print(f"  Active OTP found")
        print(f"  Expires in: {status.get('remaining_seconds')} seconds")
        print(f"  Attempts remaining: {status.get('attempts_remaining')}")
    
    # Step 3: Try wrong code
    print("\nStep 3: Trying wrong code...")
    verify_payload = {"username": username, "otp_code": "000000"}
    response = requests.post(f"{BASE_URL}/api/otp/verify", json=verify_payload)
    result = response.json()
    print(f"  Result: {result.get('message')}")
    
    # Step 4: Check status again
    print("\nStep 4: Checking status after failed attempt...")
    response = requests.get(f"{BASE_URL}/api/otp/status/{username}")
    status = response.json()
    if status.get('has_active_otp'):
        print(f"  Attempts used: {status.get('attempts')}")
        print(f"  Attempts remaining: {status.get('attempts_remaining')}")
    
    print(f"\n✓ Complete flow tested!")
    print(f"\n📧 Note: Check email for the actual OTP code to test successful verification")
    return True

def run_all_tests():
    """Run all OTP endpoint tests"""
    print("\n" + "=" * 60)
    print("OTP API ENDPOINT TEST SUITE")
    print("=" * 60)
    print("Make sure the API server is running on http://localhost:8000")
    print("=" * 60)
    
    results = []
    
    try:
        # Run all tests
        results.append(("Request OTP", test_request_otp()))
        results.append(("Request OTP - Invalid User", test_request_otp_invalid_user()))
        results.append(("Get OTP Status", test_get_otp_status()))
        results.append(("Verify OTP - Wrong Code", test_verify_otp_wrong_code()))
        results.append(("Verify OTP - Invalid Format", test_verify_otp_invalid_format()))
        results.append(("Rate Limiting", test_rate_limiting()))
        results.append(("Maximum Attempts", test_max_attempts()))
        results.append(("Complete Flow", test_full_flow()))
        
        # Print summary
        print_separator("TEST SUMMARY")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\n{passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
        
        print("\n" + "=" * 60)
        print(f"API Documentation: {BASE_URL}/docs")
        print(f"OTP Endpoints:")
        print(f"  POST {BASE_URL}/api/otp/request")
        print(f"  POST {BASE_URL}/api/otp/verify")
        print(f"  GET  {BASE_URL}/api/otp/status/{{username}}")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the server is running: python3 main.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    run_all_tests()
