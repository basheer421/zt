#!/usr/bin/env python3
"""
Create default admin account for Render deployment
This runs automatically during build
"""

import bcrypt
from database import init_db, create_admin_user, get_admin_user

# Default admin credentials
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin123!"

def create_default_admin():
    """Create default admin user if it doesn't exist"""
    print("=" * 60)
    print("CREATING DEFAULT ADMIN ACCOUNT")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Check if admin already exists
    existing = get_admin_user(DEFAULT_ADMIN_USERNAME)
    if existing:
        print(f"⚠ Admin user '{DEFAULT_ADMIN_USERNAME}' already exists - skipping")
        return
    
    # Hash password
    password_hash = bcrypt.hashpw(
        DEFAULT_ADMIN_PASSWORD.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Create admin user
    try:
        create_admin_user(DEFAULT_ADMIN_USERNAME, password_hash)
        print(f"✓ Created default admin user")
        print(f"  Username: {DEFAULT_ADMIN_USERNAME}")
        print(f"  Password: {DEFAULT_ADMIN_PASSWORD}")
        print()
        print("⚠ IMPORTANT: Change this password after first login!")
        print("=" * 60)
    except Exception as e:
        print(f"✗ Failed to create admin user: {str(e)}")

if __name__ == "__main__":
    create_default_admin()
