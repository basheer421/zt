#!/usr/bin/env python3
"""
Create test users for ML API testing
"""

import requests
import json

ADMIN_PANEL_URL = "https://wallpaper-pregnant-onion-supposed.trycloudflare.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123!"

def login_admin():
    """Login as admin and get token"""
    print("Logging in as admin...")
    response = requests.post(
        f"{ADMIN_PANEL_URL}/admin/login",
        json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"✓ Admin login successful")
        return token
    else:
        print(f"✗ Admin login failed: {response.status_code}")
        print(response.text)
        return None

def create_user(token, username, email, password):
    """Create a user via admin API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\nCreating user: {username}")
    response = requests.post(
        f"{ADMIN_PANEL_URL}/admin/users",
        headers=headers,
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    if response.status_code == 200:
        print(f"✓ User {username} created successfully")
        return True
    elif response.status_code == 400 and "already exists" in response.text:
        print(f"⚠ User {username} already exists")
        return True
    else:
        print(f"✗ Failed to create user: {response.status_code}")
        print(response.text)
        return False

def main():
    print("="*60)
    print("CREATING TEST USERS FOR ML API TESTING")
    print("="*60)
    
    # Login as admin
    token = login_admin()
    if not token:
        print("\n✗ Cannot proceed without admin token")
        return
    
    # Test users to create
    test_users = [
        {
            "username": "test_user_uae",
            "email": "test_uae@example.com",
            "password": "Test123!"
        },
        {
            "username": "test_user_foreign",
            "email": "test_foreign@example.com",
            "password": "Test123!"
        },
        {
            "username": "test_user_suspicious",
            "email": "test_suspicious@example.com",
            "password": "Test123!"
        }
    ]
    
    # Create each user
    success_count = 0
    for user in test_users:
        if create_user(token, user["username"], user["email"], user["password"]):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"COMPLETE: {success_count}/{len(test_users)} users ready")
    print("="*60)
    print("\nYou can now run: python test_ml_api.py")

if __name__ == "__main__":
    main()
