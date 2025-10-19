import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import os
from pathlib import Path

# Database configuration
DB_PATH = os.getenv("DB_PATH", "app.db")

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
    """Initialize database with tables"""
    print(f"Initializing database at {DB_PATH}")
    
    with get_db() as cursor:
        # Example users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Example predictions table for ML results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                model_name TEXT NOT NULL,
                input_data TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Example API keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                key_hash TEXT UNIQUE NOT NULL,
                name TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
    
    print("Database initialized successfully")

def close_db():
    """Close database connection"""
    global _connection
    if _connection:
        _connection.close()
        _connection = None
    print("Database connection closed")

# Database query functions

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results"""
    with get_db() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

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

# Example CRUD operations

def create_user(email: str, password_hash: str, full_name: Optional[str] = None) -> int:
    """Create a new user"""
    query = "INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)"
    return execute_insert(query, (email, password_hash, full_name))

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    query = "SELECT * FROM users WHERE email = ?"
    results = execute_query(query, (email,))
    return results[0] if results else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    query = "SELECT * FROM users WHERE id = ?"
    results = execute_query(query, (user_id,))
    return results[0] if results else None

def save_prediction(user_id: Optional[int], model_name: str, 
                   input_data: str, prediction: str, 
                   confidence: Optional[float] = None) -> int:
    """Save ML prediction result"""
    query = """
        INSERT INTO predictions (user_id, model_name, input_data, prediction, confidence)
        VALUES (?, ?, ?, ?, ?)
    """
    return execute_insert(query, (user_id, model_name, input_data, prediction, confidence))

def get_user_predictions(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user's recent predictions"""
    query = """
        SELECT * FROM predictions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """
    return execute_query(query, (user_id, limit))
