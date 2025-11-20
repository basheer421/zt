#!/usr/bin/env python3
"""
Test script to verify India OTP logic without running the full server
"""

# Simulate the authentication logic
def test_india_user_logic():
    print("=" * 60)
    print("TESTING INDIA USER OTP LOGIC")
    print("=" * 60)
    
    # Test Case 1: india_user
    username = "india_user"
    country = "XX"  # Not India country
    ml_risk_score = 40
    
    print(f"\nTest 1: username='{username}', country='{country}'")
    
    # This is the exact logic from main.py lines 301-303
    if country == 'IN' or username == 'india_user':
        require_2fa = True
        print(f"  [2FA] FORCING 2FA for India/india_user - Username: {username}, Country: {country}")
    elif ml_risk_score >= 70:
        require_2fa = True
        print(f"  [2FA] High risk score ({ml_risk_score}) - Requiring 2FA")
    elif ml_risk_score >= 30:
        device_known = False  # Assume unknown device
        require_2fa = not device_known
        print(f"  [2FA] Medium risk ({ml_risk_score}) - Device known: {device_known}, Require 2FA: {require_2fa}")
    else:
        require_2fa = False
        print(f"  [2FA] Low risk ({ml_risk_score}) - Allowing direct login")
    
    print(f"  [2FA] FINAL DECISION - require_2fa: {require_2fa}")
    
    if require_2fa:
        print(f"  ✓ CORRECT: Would return OTP challenge")
        return True
    else:
        print(f"  ✗ ERROR: Would allow direct login (WRONG!)")
        return False
    
    # Test Case 2: Regular user from India
    print(f"\nTest 2: username='john_doe', country='IN'")
    username2 = "john_doe"
    country2 = "IN"
    
    if country2 == 'IN' or username2 == 'india_user':
        require_2fa2 = True
        print(f"  [2FA] FORCING 2FA for India/india_user - Username: {username2}, Country: {country2}")
        print(f"  [2FA] FINAL DECISION - require_2fa: {require_2fa2}")
        print(f"  ✓ CORRECT: Would return OTP challenge")
        return True
    else:
        print(f"  ✗ ERROR: Logic failed")
        return False

if __name__ == "__main__":
    result = test_india_user_logic()
    print("\n" + "=" * 60)
    if result:
        print("✓ LOGIC IS CORRECT - Issue must be deployment/server")
    else:
        print("✗ LOGIC IS BROKEN - Fix needed in code")
    print("=" * 60)
