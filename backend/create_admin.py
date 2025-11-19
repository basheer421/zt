"""
Script to create an initial admin user for the ZT-Verify admin panel
"""
import bcrypt
import sys
import os

# Add parent directory to path so we can import database
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, create_admin_user, get_admin_user

def main():
    print("=" * 60)
    print("ZT-Verify Admin User Creation")
    print("=" * 60)
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    # Get username and password
    username = input("\nEnter admin username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        return
    
    # Check if admin already exists
    existing = get_admin_user(username)
    if existing:
        print(f"Error: Admin user '{username}' already exists")
        return
    
    password = input("Enter admin password (min 6 characters): ").strip()
    if len(password) < 6:
        print("Error: Password must be at least 6 characters")
        return
    
    confirm_password = input("Confirm password: ").strip()
    if password != confirm_password:
        print("Error: Passwords do not match")
        return
    
    # Hash password
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Create admin user
    admin_id = create_admin_user(username, password_hash)
    
    print("\n" + "=" * 60)
    print(f"✓ Admin user created successfully!")
    print(f"  Username: {username}")
    print(f"  ID: {admin_id}")
    print("=" * 60)
    print("\nYou can now login to the admin panel with these credentials.")

if __name__ == "__main__":
    main()
