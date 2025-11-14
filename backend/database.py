import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_PATH = os.getenv("DB_PATH", "zt_verify.db")

# Global connection pool
_connection = None

def get_connection():
    """Get or create database connection"""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    return _connection

@contextmanager
def get_db():
    """Context manager for database operations"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

def init_db():
    """Initialize database with ZT-Verify tables"""
    print(f"Initializing ZT-Verify database at {DB_PATH}")
    
    with get_db() as cursor:
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'viewer' CHECK(role IN ('admin', 'manager', 'viewer')),
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'locked', 'suspended')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add role column if it doesn't exist (migration for existing databases)
        cursor.execute("""
            SELECT COUNT(*) as count FROM pragma_table_info('users') WHERE name='role'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'viewer' CHECK(role IN ('admin', 'manager', 'viewer'))
            """)
            print("✅ Added 'role' column to users table")
        
        # Login attempts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                device_fingerprint TEXT,
                location TEXT,
                risk_score REAL,
                action TEXT CHECK(action IN ('allow', 'deny', 'challenge', 'review')),
                success BOOLEAN DEFAULT 0
            )
        """)
        
        # OTP codes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                attempts INTEGER DEFAULT 0,
                verified BOOLEAN DEFAULT 0
            )
        """)
        
        # User devices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                device_fingerprint TEXT NOT NULL,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(username, device_fingerprint)
            )
        """)
        
        # Admin users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Inventory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                unit TEXT NOT NULL,
                location TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_login_attempts_username 
            ON login_attempts(username)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_login_attempts_timestamp 
            ON login_attempts(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_otp_codes_username 
            ON otp_codes(username)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_devices_username 
            ON user_devices(username)
        """)
    
    print("ZT-Verify database initialized successfully")

def close_db():
    """Close database connection"""
    global _connection
    if _connection:
        _connection.close()
        _connection = None
    print("Database connection closed")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results as list of dicts"""
    with get_db() as cursor:
        cursor.execute(query, params)
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return []

def execute_insert(query: str, params: tuple = ()) -> int:
    """Execute an INSERT query and return the last inserted row ID"""
    with get_db() as cursor:
        cursor.execute(query, params)
        return cursor.lastrowid

def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an UPDATE/DELETE query and return affected rows"""
    with get_db() as cursor:
        cursor.execute(query, params)
        return cursor.rowcount

# ============================================================================
# USER FUNCTIONS
# ============================================================================

def create_user(username: str, password_hash: str, email: str, role: str = 'viewer', status: str = 'active') -> int:
    """
    Create a new user
    
    Args:
        username: Unique username
        password_hash: Hashed password
        email: User email address
        role: User role (admin, manager, viewer)
        status: User status (active, inactive, locked, suspended)
    
    Returns:
        User ID of the created user
    """
    query = """
        INSERT INTO users (username, password_hash, email, role, status) 
        VALUES (?, ?, ?, ?, ?)
    """
    return execute_insert(query, (username, password_hash, email, role, status))

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user by username
    
    Args:
        username: Username to look up
    
    Returns:
        User dict or None if not found
    """
    query = "SELECT * FROM users WHERE username = ?"
    results = execute_query(query, (username,))
    return results[0] if results else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    query = "SELECT * FROM users WHERE id = ?"
    results = execute_query(query, (user_id,))
    return results[0] if results else None

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    query = "SELECT * FROM users WHERE email = ?"
    results = execute_query(query, (email,))
    return results[0] if results else None

def update_user_status(username: str, status: str) -> int:
    """Update user status"""
    query = "UPDATE users SET status = ? WHERE username = ?"
    return execute_update(query, (status, username))

def update_user_role(user_id: int, role: str) -> int:
    """Update user role"""
    query = "UPDATE users SET role = ? WHERE id = ?"
    return execute_update(query, (role, user_id))

def list_all_users() -> List[Dict[str, Any]]:
    """Get all users"""
    query = "SELECT id, username, email, role, status, created_at FROM users ORDER BY created_at DESC"
    return execute_query(query)

# ============================================================================
# LOGIN ATTEMPT FUNCTIONS
# ============================================================================

def log_login_attempt(
    username: str,
    ip_address: str,
    device_fingerprint: str,
    location: Optional[str] = None,
    risk_score: Optional[float] = None,
    action: str = 'allow',
    success: bool = False
) -> int:
    """
    Log a login attempt
    
    Args:
        username: Username attempting to login
        ip_address: IP address of the request
        device_fingerprint: Device fingerprint hash
        location: Geographic location (optional)
        risk_score: ML model risk score (0-1)
        action: Action taken (allow, deny, challenge, review)
        success: Whether login was successful
    
    Returns:
        ID of the logged attempt
    """
    query = """
        INSERT INTO login_attempts 
        (username, ip_address, device_fingerprint, location, risk_score, action, success)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    return execute_insert(query, (
        username, ip_address, device_fingerprint, location, 
        risk_score, action, success
    ))

def get_user_history(username: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get login history for a user
    
    Args:
        username: Username to get history for
        limit: Maximum number of records to return
    
    Returns:
        List of login attempt records
    """
    query = """
        SELECT * FROM login_attempts 
        WHERE username = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """
    return execute_query(query, (username, limit))

def get_recent_failed_attempts(username: str, minutes: int = 15) -> List[Dict[str, Any]]:
    """Get recent failed login attempts for a user"""
    query = """
        SELECT * FROM login_attempts 
        WHERE username = ? 
        AND success = 0 
        AND timestamp >= datetime('now', '-' || ? || ' minutes')
        ORDER BY timestamp DESC
    """
    return execute_query(query, (username, minutes))

def count_failed_attempts(username: str, minutes: int = 15) -> int:
    """Count failed login attempts in the last N minutes"""
    attempts = get_recent_failed_attempts(username, minutes)
    return len(attempts)

def get_all_login_attempts(limit: int = 100) -> List[Dict[str, Any]]:
    """Get all login attempts (for admin panel)"""
    query = """
        SELECT * FROM login_attempts 
        ORDER BY timestamp DESC 
        LIMIT ?
    """
    return execute_query(query, (limit,))

def get_high_risk_attempts(threshold: float = 0.7, limit: int = 50) -> List[Dict[str, Any]]:
    """Get high-risk login attempts"""
    query = """
        SELECT * FROM login_attempts 
        WHERE risk_score >= ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """
    return execute_query(query, (threshold, limit))

# ============================================================================
# OTP FUNCTIONS
# ============================================================================

def store_otp(username: str, code: str, expires_in_minutes: int = 10) -> int:
    """
    Store an OTP code for a user
    
    Args:
        username: Username for the OTP
        code: OTP code (should be hashed in production)
        expires_in_minutes: Expiration time in minutes
    
    Returns:
        ID of the stored OTP
    """
    # Calculate expiration time
    expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
    
    query = """
        INSERT INTO otp_codes (username, code, expires_at)
        VALUES (?, ?, ?)
    """
    return execute_insert(query, (username, code, expires_at.isoformat()))

def verify_otp(username: str, code: str) -> Dict[str, Any]:
    """
    Verify an OTP code
    
    Args:
        username: Username to verify OTP for
        code: OTP code to verify
    
    Returns:
        Dict with 'valid' boolean and 'message' string
    """
    # Get the most recent unverified OTP for this user
    query = """
        SELECT * FROM otp_codes 
        WHERE username = ? 
        AND verified = 0 
        ORDER BY created_at DESC 
        LIMIT 1
    """
    results = execute_query(query, (username,))
    
    if not results:
        return {'valid': False, 'message': 'No OTP found'}
    
    otp = results[0]
    
    # Check if expired
    expires_at = datetime.fromisoformat(otp['expires_at'])
    if datetime.now() > expires_at:
        return {'valid': False, 'message': 'OTP expired'}
    
    # Check attempts
    if otp['attempts'] >= 3:
        return {'valid': False, 'message': 'Too many attempts'}
    
    # Verify code
    if otp['code'] == code:
        # Mark as verified
        update_query = "UPDATE otp_codes SET verified = 1 WHERE id = ?"
        execute_update(update_query, (otp['id'],))
        return {'valid': True, 'message': 'OTP verified successfully'}
    else:
        # Increment attempts
        update_query = "UPDATE otp_codes SET attempts = attempts + 1 WHERE id = ?"
        execute_update(update_query, (otp['id'],))
        return {'valid': False, 'message': 'Invalid OTP code'}

def invalidate_user_otps(username: str) -> int:
    """Invalidate all OTPs for a user"""
    query = "UPDATE otp_codes SET verified = 1 WHERE username = ? AND verified = 0"
    return execute_update(query, (username,))

def get_active_otp(username: str) -> Optional[Dict[str, Any]]:
    """Get active (unverified, not expired) OTP for a user"""
    query = """
        SELECT * FROM otp_codes 
        WHERE username = ? 
        AND verified = 0 
        AND expires_at > datetime('now')
        ORDER BY created_at DESC 
        LIMIT 1
    """
    results = execute_query(query, (username,))
    return results[0] if results else None

# ============================================================================
# USER DEVICE FUNCTIONS
# ============================================================================

def register_device(username: str, device_fingerprint: str) -> int:
    """
    Register or update a device for a user
    
    Args:
        username: Username
        device_fingerprint: Unique device fingerprint
    
    Returns:
        Device ID
    """
    # Check if device already exists
    query = "SELECT id FROM user_devices WHERE username = ? AND device_fingerprint = ?"
    results = execute_query(query, (username, device_fingerprint))
    
    if results:
        # Update last_seen
        update_query = """
            UPDATE user_devices 
            SET last_seen = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        execute_update(update_query, (results[0]['id'],))
        return results[0]['id']
    else:
        # Insert new device
        insert_query = """
            INSERT INTO user_devices (username, device_fingerprint)
            VALUES (?, ?)
        """
        return execute_insert(insert_query, (username, device_fingerprint))

def is_known_device(username: str, device_fingerprint: str) -> bool:
    """Check if a device is known for a user"""
    query = """
        SELECT id FROM user_devices 
        WHERE username = ? AND device_fingerprint = ?
    """
    results = execute_query(query, (username, device_fingerprint))
    return len(results) > 0

def get_user_devices(username: str) -> List[Dict[str, Any]]:
    """Get all devices for a user"""
    query = """
        SELECT * FROM user_devices 
        WHERE username = ? 
        ORDER BY last_seen DESC
    """
    return execute_query(query, (username,))

def remove_device(username: str, device_fingerprint: str) -> int:
    """Remove a device from a user's trusted devices"""
    query = "DELETE FROM user_devices WHERE username = ? AND device_fingerprint = ?"
    return execute_update(query, (username, device_fingerprint))

# ============================================================================
# ADMIN USER FUNCTIONS
# ============================================================================

def create_admin_user(username: str, password_hash: str) -> int:
    """Create an admin user"""
    query = "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)"
    return execute_insert(query, (username, password_hash))

def get_admin_user(username: str) -> Optional[Dict[str, Any]]:
    """Get admin user by username"""
    query = "SELECT * FROM admin_users WHERE username = ?"
    results = execute_query(query, (username,))
    return results[0] if results else None

def list_admin_users() -> List[Dict[str, Any]]:
    """Get all admin users"""
    query = "SELECT id, username, created_at FROM admin_users ORDER BY created_at DESC"
    return execute_query(query)

def delete_admin_user(username: str) -> int:
    """Delete an admin user"""
    query = "DELETE FROM admin_users WHERE username = ?"
    return execute_update(query, (username,))

# ============================================================================
# ANALYTICS & REPORTING FUNCTIONS
# ============================================================================

def get_login_stats(days: int = 7) -> Dict[str, Any]:
    """Get login statistics for the last N days"""
    query = """
        SELECT 
            COUNT(*) as total_attempts,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_logins,
            SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_logins,
            COUNT(DISTINCT username) as unique_users,
            AVG(risk_score) as avg_risk_score
        FROM login_attempts
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
    """
    results = execute_query(query, (days,))
    return results[0] if results else {}

def get_top_risky_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Get users with highest average risk scores"""
    query = """
        SELECT 
            username,
            COUNT(*) as attempt_count,
            AVG(risk_score) as avg_risk_score,
            MAX(timestamp) as last_attempt
        FROM login_attempts
        WHERE risk_score IS NOT NULL
        GROUP BY username
        ORDER BY avg_risk_score DESC
        LIMIT ?
    """
    return execute_query(query, (limit,))
