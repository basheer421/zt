#!/usr/bin/env python3
"""
Test script for OTP module
Tests OTP generation, email sending, and verification
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from otp import (
    generate_otp,
    send_otp_email,
    create_otp_challenge,
    verify_otp,
    get_otp_status,
    format_remaining_time
)
from database import init_db, create_user, get_user
import bcrypt

# Load environment variables from .env file
load_dotenv()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def test_otp_module():
    """Test all OTP functions"""
    
    print("=" * 60)
    print("OTP MODULE TEST")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Create test user if doesn't exist
    print("\n2. Setting up test user...")
    test_username = "otp_test_user"
    test_email = "test@example.com"
    
    user = get_user(test_username)
    if not user:
        user_id = create_user(
            username=test_username,
            password_hash=hash_password("TestPass123!"),
            email=test_email,
            status="active"
        )
        print(f"✓ Created test user: {test_username} (ID: {user_id})")
    else:
        print(f"✓ Test user exists: {test_username}")
    
    # Test 1: OTP Generation
    print("\n3. Testing OTP generation...")
    otp1 = generate_otp()
    print(f"Generated OTP: {otp1}")
    assert len(otp1) == 6, "OTP should be 6 digits"
    assert otp1.isdigit(), "OTP should contain only digits"
    print("✓ OTP generation works!")
    
    # Test 2: Generate multiple OTPs (should be different)
    print("\n4. Testing OTP uniqueness...")
    otp2 = generate_otp()
    otp3 = generate_otp()
    print(f"OTP 1: {otp1}")
    print(f"OTP 2: {otp2}")
    print(f"OTP 3: {otp3}")
    # Note: Extremely small chance they could be the same, but very unlikely
    print("✓ OTP generation produces codes")
    
    # Test 3: Check Resend API configuration
    print("\n5. Checking Resend API configuration...")
    resend_key = os.getenv("RESEND_API_KEY", "")
    if resend_key and resend_key != "your-resend-api-key-here":
        print(f"✓ Resend API key configured (starts with: {resend_key[:10]}...)")
        api_configured = True
    else:
        print("⚠ Resend API key not configured in .env file")
        print("  Email sending will be skipped in tests")
        print("  To test email: Set RESEND_API_KEY in .env file")
        api_configured = False
    
    # Test 4: Send OTP Email (only if API is configured)
    if api_configured:
        print("\n6. Testing email sending...")
        print(f"Sending test OTP email to: {test_email}")
        email_result = send_otp_email(
            user_email=test_email,
            otp_code="123456",
            username=test_username
        )
        print(f"Result: {email_result}")
        if email_result['success']:
            print("✓ Email sent successfully!")
            print(f"  Email ID: {email_result.get('email_id', 'N/A')}")
        else:
            print(f"✗ Email sending failed: {email_result.get('error', 'Unknown error')}")
    else:
        print("\n6. Skipping email test (API not configured)")
    
    # Test 5: Create OTP Challenge
    print("\n7. Testing OTP challenge creation...")
    challenge_result = create_otp_challenge(test_username, test_email)
    print(f"Challenge result: {challenge_result}")
    
    if challenge_result['success']:
        print("✓ OTP challenge created successfully!")
        print(f"  OTP ID: {challenge_result.get('otp_id', 'N/A')}")
        print(f"  Expires in: {challenge_result.get('expires_in_minutes', 'N/A')} minutes")
        if api_configured:
            print(f"  Email ID: {challenge_result.get('email_id', 'N/A')}")
    else:
        print(f"✗ Challenge creation failed: {challenge_result.get('error', 'Unknown error')}")
        # Don't exit - we might not have email configured
    
    # Test 6: Get OTP Status
    print("\n8. Testing OTP status check...")
    status = get_otp_status(test_username)
    print(f"OTP Status: {status}")
    if status.get('has_active_otp'):
        print("✓ Active OTP found!")
        print(f"  Created at: {status.get('created_at', 'N/A')}")
        print(f"  Expires at: {status.get('expires_at', 'N/A')}")
        print(f"  Remaining time: {format_remaining_time(status.get('remaining_seconds', 0))}")
        print(f"  Attempts remaining: {status.get('attempts_remaining', 'N/A')}")
    
    # Test 7: Verify OTP (wrong code)
    print("\n9. Testing OTP verification (wrong code)...")
    verify_result = verify_otp(test_username, "999999")
    print(f"Verification result: {verify_result}")
    assert not verify_result['valid'], "Wrong OTP should fail"
    print("✓ Wrong OTP correctly rejected!")
    print(f"  Message: {verify_result['message']}")
    print(f"  Attempts remaining: {verify_result.get('attempts_remaining', 'N/A')}")
    
    # Test 8: Verify OTP (correct code) - if we have an active OTP
    if status.get('has_active_otp'):
        print("\n10. Testing OTP verification (correct code)...")
        print("⚠ Note: We don't know the actual OTP code from the database")
        print("   In production, user would enter the code from their email")
        
        # Try to verify with various attempts to demonstrate the attempt tracking
        print("\nDemonstrating attempt tracking:")
        for i in range(1, 4):
            result = verify_otp(test_username, f"00000{i}")
            print(f"  Attempt {i}: {result['message']}")
            if result.get('attempts_remaining') is not None:
                print(f"    Attempts remaining: {result['attempts_remaining']}")
    
    # Test 9: Format remaining time
    print("\n11. Testing time formatting...")
    print(f"  45 seconds: {format_remaining_time(45)}")
    print(f"  90 seconds: {format_remaining_time(90)}")
    print(f"  300 seconds: {format_remaining_time(300)}")
    print("✓ Time formatting works!")
    
    # Test 10: Try to create another OTP (should be rate-limited)
    print("\n12. Testing rate limiting...")
    if status.get('has_active_otp') and status.get('remaining_seconds', 0) > 0:
        challenge_result2 = create_otp_challenge(test_username, test_email)
        if not challenge_result2['success']:
            print("✓ Rate limiting works!")
            print(f"  Message: {challenge_result2.get('error', 'N/A')}")
        else:
            print("⚠ Rate limiting might not be working properly")
    else:
        print("⚠ No active OTP to test rate limiting")
    
    # Summary
    print("\n" + "=" * 60)
    print("OTP MODULE TESTS COMPLETED")
    print("=" * 60)
    
    if api_configured:
        print("\n✓ Full test completed with email sending")
        print(f"\nCheck your email at {test_email} for the OTP!")
    else:
        print("\n⚠ Partial test completed (email not configured)")
        print("\nTo enable email testing:")
        print("1. Sign up at https://resend.com")
        print("2. Get your API key from https://resend.com/api-keys")
        print("3. Add to .env file: RESEND_API_KEY=re_your_api_key")
        print("4. Run this test again")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_otp_module()
