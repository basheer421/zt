from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, List
import bcrypt
import jwt
from datetime import datetime, timedelta

from database import (
    get_admin_user,
    create_admin_user,
    list_admin_users,
    delete_admin_user,
    list_all_users,
    update_user_status,
    get_user,
    create_user,
    get_all_login_attempts,
    get_user_history,
    get_login_stats,
    get_top_risky_users,
)

# Router for admin endpoints
router = APIRouter(prefix="/api/admin", tags=["Admin"])

# JWT Secret (in production, use environment variable)
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    token: str
    username: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str
    role: str = 'viewer'  # Default to viewer role

class UpdateUserStatusRequest(BaseModel):
    status: str

class UpdateUserRoleRequest(BaseModel):
    role: str

class CreateAdminRequest(BaseModel):
    username: str
    password: str

# ============================================================================
# AUTH HELPER
# ============================================================================

def verify_admin_token(authorization: Optional[str] = Header(None)) -> str:
    """Verify JWT token and return username"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("username")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# ADMIN AUTH ENDPOINTS
# ============================================================================

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint"""
    admin = get_admin_user(request.username)
    
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    password_match = bcrypt.checkpw(
        request.password.encode('utf-8'),
        admin['password_hash'].encode('utf-8')
    )
    
    if not password_match:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    token_data = {
        "username": request.username,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return AdminLoginResponse(token=token, username=request.username)

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/stats")
async def get_stats(
    days: int = 7,
    admin_username: str = Depends(verify_admin_token)
):
    """Get dashboard statistics"""
    stats = get_login_stats(days)
    
    # Get user counts
    all_users = list_all_users()
    total_users = len(all_users)
    active_users = len([u for u in all_users if u['status'] == 'active'])
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_attempts": stats.get('total_attempts', 0),
        "successful_logins": stats.get('successful_logins', 0),
        "failed_logins": stats.get('failed_logins', 0),
        "unique_users": stats.get('unique_users', 0),
        "avg_risk_score": stats.get('avg_risk_score', 0.0),
    }

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    admin_username: str = Depends(verify_admin_token)
):
    """Get recent login attempts"""
    attempts = get_all_login_attempts(limit)
    return attempts

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/users")
async def get_all_users(admin_username: str = Depends(verify_admin_token)):
    """Get all users"""
    return list_all_users()

@router.get("/users/{user_id}")
async def get_user_by_id(
    user_id: int,
    admin_username: str = Depends(verify_admin_token)
):
    """Get user by ID"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users")
async def create_new_user(
    request: CreateUserRequest,
    admin_username: str = Depends(verify_admin_token)
):
    """Create a new user"""
    # Check if user already exists
    existing = get_user(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Validate role
    if request.role not in ['admin', 'manager', 'viewer']:
        raise HTTPException(status_code=400, detail="Invalid role. Must be: admin, manager, or viewer")
    
    # Hash password
    password_hash = bcrypt.hashpw(
        request.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Create user with role
    user_id = create_user(request.username, password_hash, request.email, role=request.role, status='active')
    
    return {
        "id": user_id,
        "username": request.username,
        "email": request.email,
        "role": request.role,
        "password": request.password,  # Return plain password so admin can share it
        "status": "active",
        "message": "User created successfully. Share these credentials with the user."
    }

@router.patch("/users/{user_id}/status")
async def update_user_status_endpoint(
    user_id: int,
    request: UpdateUserStatusRequest,
    admin_username: str = Depends(verify_admin_token)
):
    """Update user status"""
    from database import get_user_by_id, execute_update
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update status
    query = "UPDATE users SET status = ? WHERE id = ?"
    execute_update(query, (request.status, user_id))
    
    return {"success": True, "message": "User status updated"}

@router.patch("/users/{user_id}/role")
async def update_user_role_endpoint(
    user_id: int,
    request: UpdateUserRoleRequest,
    admin_username: str = Depends(verify_admin_token)
):
    """Update user role"""
    from database import get_user_by_id, update_user_role
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate role
    if request.role not in ['admin', 'manager', 'viewer']:
        raise HTTPException(status_code=400, detail="Invalid role. Must be: admin, manager, or viewer")
    
    # Update role
    update_user_role(user_id, request.role)
    
    return {"success": True, "message": "User role updated"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_username: str = Depends(verify_admin_token)
):
    """Delete a user"""
    from database import get_user_by_id, execute_update
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete user
    query = "DELETE FROM users WHERE id = ?"
    execute_update(query, (user_id,))
    
    return {"success": True, "message": "User deleted"}

# ============================================================================
# LOGIN ATTEMPTS ENDPOINTS
# ============================================================================

@router.get("/login-attempts")
async def get_login_attempts(
    username: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    admin_username: str = Depends(verify_admin_token)
):
    """Get login attempts with optional filtering"""
    if username:
        # Get attempts for specific user
        from database import execute_query
        query = """
            SELECT * FROM login_attempts 
            WHERE username = ? 
            AND timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        attempts = execute_query(query, (username, days, limit))
    else:
        # Get all recent attempts
        from database import execute_query
        query = """
            SELECT * FROM login_attempts 
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        attempts = execute_query(query, (days, limit))
    
    return attempts

@router.get("/login-attempts/{username}")
async def get_user_login_attempts(
    username: str,
    days: int = 30,
    admin_username: str = Depends(verify_admin_token)
):
    """Get login attempts for a specific user"""
    from database import execute_query
    query = """
        SELECT * FROM login_attempts 
        WHERE username = ? 
        AND timestamp >= datetime('now', '-' || ? || ' days')
        ORDER BY timestamp DESC
    """
    attempts = execute_query(query, (username, days))
    return attempts

# ============================================================================
# RISK ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/risky-users")
async def get_risky_users(
    limit: int = 10,
    admin_username: str = Depends(verify_admin_token)
):
    """Get top risky users"""
    return get_top_risky_users(limit)

@router.get("/risk-distribution")
async def get_risk_distribution(
    days: int = 7,
    admin_username: str = Depends(verify_admin_token)
):
    """Get risk score distribution"""
    from database import execute_query
    
    query = """
        SELECT 
            CASE 
                WHEN risk_score < 0.3 THEN 'Low'
                WHEN risk_score < 0.7 THEN 'Medium'
                ELSE 'High'
            END as risk_level,
            COUNT(*) as count
        FROM login_attempts
        WHERE risk_score IS NOT NULL
        AND timestamp >= datetime('now', '-' || ? || ' days')
        GROUP BY risk_level
    """
    distribution = execute_query(query, (days,))
    return distribution

# ============================================================================
# ADMIN USER MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/admin-users")
async def get_admin_users(admin_username: str = Depends(verify_admin_token)):
    """Get all admin users"""
    return list_admin_users()

@router.post("/admin-users")
async def create_admin(
    request: CreateAdminRequest,
    admin_username: str = Depends(verify_admin_token)
):
    """Create a new admin user"""
    # Check if admin already exists
    existing = get_admin_user(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Admin username already exists")
    
    # Hash password
    password_hash = bcrypt.hashpw(
        request.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Create admin
    admin_id = create_admin_user(request.username, password_hash)
    
    return {
        "id": admin_id,
        "username": request.username,
        "created_at": datetime.now().isoformat()
    }

@router.delete("/admin-users/{username}")
async def delete_admin(
    username: str,
    admin_username: str = Depends(verify_admin_token)
):
    """Delete an admin user"""
    # Don't allow deleting yourself
    if username == admin_username:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")
    
    admin = get_admin_user(username)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    delete_admin_user(username)
    
    return {"success": True, "message": "Admin user deleted"}
