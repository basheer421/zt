#!/usr/bin/env python3
"""
Quick script to create india_user for testing India OTP requirement
"""

import bcrypt
from database import init_db, create_user, get_user

def create_india_user():
    print("Creating india_user...")
    
    # Initialize database
    init_db()
    
    username = 'india_user'
    password = 'Test123!'
    email = 'india@example.com'
    
    # Check if user already exists
    existing_user = get_user(username)
    if existing_user:
        print(f"✓ User '{username}' already exists")
        return
    
    # Hash the password
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Create the user
    try:
        create_user(username, password_hash, email, status='active')
        print(f"✓ Created user: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  This user will ALWAYS require OTP (simulates India login)")
    except Exception as e:
        print(f"✗ Failed to create user: {str(e)}")

if __name__ == "__main__":
    create_india_user()
