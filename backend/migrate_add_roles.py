#!/usr/bin/env python3
"""
Migration script to add default roles to existing users
Run this after updating the database schema
"""

from database import init_db, execute_update

def migrate_user_roles():
    """Add default role to existing users without a role"""
    print("Starting role migration...")
    
    # Initialize database (will add role column if needed)
    init_db()
    
    # Update all users without a role to have 'viewer' role
    query = "UPDATE users SET role = 'viewer' WHERE role IS NULL OR role = ''"
    rows_updated = execute_update(query)
    
    print(f"✅ Updated {rows_updated} users with default 'viewer' role")
    print("Migration complete!")

if __name__ == "__main__":
    migrate_user_roles()
