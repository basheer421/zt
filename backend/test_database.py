#!/usr/bin/env python3
"""
Test script for ZT-Verify database functions
Run this to test the database setup and functions
"""

import os
import bcrypt
from database import (
    init_db, 
    create_user, 
    get_user,
    log_login_attempt,
    get_user_history,
    store_otp,
    verify_otp,
    register_device,
    is_known_device,
    get_user_devices,
    create_admin_user,
    get_admin_user,
    get_login_stats,
    count_failed_attempts
)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def test_database():
    """Test all database functions"""
    
    print("=" * 60)
    print("ZT-VERIFY DATABASE TEST")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Create test users
    print("\n2. Creating test users...")
    user1_id = create_user(
        username="john_doe",
        password_hash=hash_password("SecurePass123!"),
        email="john@example.com",
        status="active"
    )
    print(f"✓ Created user: john_doe (ID: {user1_id})")
    
    user2_id = create_user(
        username="jane_smith",
        password_hash=hash_password("AnotherPass456!"),
        email="jane@example.com",
        status="active"
    )
    print(f"✓ Created user: jane_smith (ID: {user2_id})")
    
    # Get user
    print("\n3. Retrieving user...")
    user = get_user("john_doe")
    if user:
        print(f"✓ Found user: {user['username']} ({user['email']})")
        print(f"  Status: {user['status']}")
        print(f"  Created: {user['created_at']}")
    
    # Log login attempts
    print("\n4. Logging login attempts...")
    attempt1 = log_login_attempt(
        username="john_doe",
        ip_address="192.168.1.100",
        device_fingerprint="device_123abc",
        location="New York, US",
        risk_score=0.15,
        action="allow",
        success=True
    )
    print(f"✓ Logged successful login (ID: {attempt1})")
    
    attempt2 = log_login_attempt(
        username="john_doe",
        ip_address="10.0.0.50",
        device_fingerprint="device_456def",
        location="London, UK",
        risk_score=0.85,
        action="challenge",
        success=False
    )
    print(f"✓ Logged suspicious attempt (ID: {attempt2})")
    
    # Get user history
    print("\n5. Getting user login history...")
    history = get_user_history("john_doe")
    print(f"✓ Found {len(history)} login attempts")
    for h in history:
        print(f"  - {h['timestamp']}: IP={h['ip_address']}, Risk={h['risk_score']}, Success={h['success']}")
    
    # Store OTP
    print("\n6. Storing OTP code...")
    otp_id = store_otp("john_doe", "123456", expires_in_minutes=10)
    print(f"✓ Stored OTP (ID: {otp_id})")
    
    # Verify OTP (wrong code)
    print("\n7. Verifying OTP...")
    result = verify_otp("john_doe", "999999")
    print(f"  Wrong code: {result}")
    
    # Verify OTP (correct code)
    result = verify_otp("john_doe", "123456")
    print(f"  Correct code: {result}")
    
    # Register device
    print("\n8. Registering device...")
    device_id = register_device("john_doe", "device_123abc")
    print(f"✓ Registered device (ID: {device_id})")
    
    # Check known device
    print("\n9. Checking device trust...")
    is_known = is_known_device("john_doe", "device_123abc")
    print(f"✓ Device device_123abc is known: {is_known}")
    
    is_unknown = is_known_device("john_doe", "device_unknown")
    print(f"✓ Device device_unknown is known: {is_unknown}")
    
    # Get user devices
    print("\n10. Getting user devices...")
    devices = get_user_devices("john_doe")
    print(f"✓ Found {len(devices)} device(s)")
    for d in devices:
        print(f"  - {d['device_fingerprint']}: First seen {d['first_seen']}, Last seen {d['last_seen']}")
    
    # Create admin user
    print("\n11. Creating admin user...")
    admin_id = create_admin_user(
        username="admin",
        password_hash=hash_password("AdminPass789!")
    )
    print(f"✓ Created admin user (ID: {admin_id})")
    
    # Get admin user
    admin = get_admin_user("admin")
    if admin:
        print(f"✓ Found admin: {admin['username']}")
    
    # Get login statistics
    print("\n12. Getting login statistics...")
    stats = get_login_stats(days=7)
    print(f"✓ Statistics (last 7 days):")
    print(f"  Total attempts: {stats.get('total_attempts', 0)}")
    print(f"  Successful: {stats.get('successful_logins', 0)}")
    print(f"  Failed: {stats.get('failed_logins', 0)}")
    print(f"  Unique users: {stats.get('unique_users', 0)}")
    print(f"  Avg risk score: {stats.get('avg_risk_score', 0):.2f}")
    
    # Count failed attempts
    print("\n13. Counting recent failed attempts...")
    failed_count = count_failed_attempts("john_doe", minutes=15)
    print(f"✓ Failed attempts in last 15 minutes: {failed_count}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nDatabase file: {os.getenv('DB_PATH', 'zt_verify.db')}")
    print("You can now use these functions in your FastAPI application.")

if __name__ == "__main__":
    test_database()
