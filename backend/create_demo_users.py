#!/usr/bin/env python3
"""
Create demo users with hardcoded risk levels
Run this script to create green_user, yellow_user, and red_user for testing
"""

import bcrypt
from database import init_db, create_user, get_user

# Demo user configuration
DEMO_USERS = [
    {
        'username': 'green_user',
        'email': 'green@example.com',
        'role': 'user',
        'description': 'Low risk demo user (GREEN) - Risk Score: 15'
    },
    {
        'username': 'yellow_user',
        'email': 'yellow@example.com',
        'role': 'user',
        'description': 'Medium risk demo user (YELLOW) - Risk Score: 50'
    },
    {
        'username': 'red_user',
        'email': 'red@example.com',
        'role': 'user',
        'description': 'High risk demo user (RED) - Risk Score: 85'
    }
]

DEFAULT_PASSWORD = "Test123!"

def create_demo_users():
    """Create all demo users"""
    print("=" * 60)
    print("CREATING DEMO USERS")
    print("=" * 60)
    
    # Initialize database
    init_db()
    print("✓ Database initialized\n")
    
    # Create each demo user
    for user_config in DEMO_USERS:
        username = user_config['username']
        email = user_config['email']
        role = user_config['role']
        description = user_config['description']
        
        # Check if user already exists
        existing_user = get_user(username)
        if existing_user:
            print(f"⚠ User '{username}' already exists - skipping")
            continue
        
        # Hash the password
        password_hash = bcrypt.hashpw(
            DEFAULT_PASSWORD.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create the user
        try:
            create_user(username, password_hash, email, status='active')
            print(f"✓ Created user: {username}")
            print(f"  Email: {email}")
            print(f"  Password: {DEFAULT_PASSWORD}")
            print(f"  {description}")
            print()
        except Exception as e:
            print(f"✗ Failed to create user '{username}': {str(e)}")
    
    print("=" * 60)
    print("DEMO USERS CREATED SUCCESSFULLY!")
    print("=" * 60)
    print("\nRisk Level Thresholds:")
    print("  🟢 LOW (0-29):    Direct login allowed")
    print("  🟡 MEDIUM (30-69): 2FA required for unknown devices")
    print("  🔴 HIGH (70-100):  Always requires 2FA")
    print("\nLogin Credentials:")
    print(f"  Username: green_user, yellow_user, or red_user")
    print(f"  Password: {DEFAULT_PASSWORD}")
    print("\nTest the API at: http://localhost:8000/docs")

if __name__ == "__main__":
    create_demo_users()
