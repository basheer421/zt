#!/usr/bin/env python3
"""
Migration script to update yellow_user email
Updates the email from yellow@example.com to nvx.naj@gmail.com
"""

from database import init_db, get_user, execute_update

def migrate_yellow_user_email():
    """Update yellow_user email in the database"""
    print("=" * 60)
    print("MIGRATING YELLOW USER EMAIL")
    print("=" * 60)
    
    # Initialize database connection
    init_db()
    print("✓ Database initialized\n")
    
    # Check if yellow_user exists
    username = 'yellow_user'
    user = get_user(username)
    
    if not user:
        print(f"⚠ User '{username}' does not exist in database")
        print("  Run create_demo_users.py first to create the user")
        return
    
    # Show current email
    current_email = user.get('email')
    print(f"Current email for '{username}': {current_email}")
    
    # Update to new email
    new_email = 'nvx.naj@gmail.com'
    
    if current_email == new_email:
        print(f"✓ Email is already set to {new_email}")
        return
    
    # Perform the update
    query = "UPDATE users SET email = ? WHERE username = ?"
    rows_affected = execute_update(query, (new_email, username))
    
    if rows_affected > 0:
        print(f"✓ Successfully updated email to: {new_email}")
        print(f"  Rows affected: {rows_affected}")
        
        # Verify the change
        updated_user = get_user(username)
        if updated_user and updated_user.get('email') == new_email:
            print("✓ Migration verified successfully!")
        else:
            print("⚠ Warning: Could not verify the migration")
    else:
        print(f"✗ Failed to update email - no rows affected")
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    try:
        migrate_yellow_user_email()
    except Exception as e:
        print(f"\n✗ Migration failed with error: {str(e)}")
        raise
