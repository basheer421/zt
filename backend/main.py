from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import bcrypt
from datetime import datetime

from database import (
    init_db, 
    close_db,
    get_user,
    log_login_attempt,
    register_device,
    is_known_device
)
from ml_engine import load_models

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AuthenticateRequest(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    timestamp: str = Field(..., description="Login timestamp")
    device_fingerprint: str = Field(..., description="Unique device identifier")
    ip_address: str = Field(..., description="Client IP address")
    location: Optional[str] = Field(None, description="Geographic location")

class AuthenticateResponse(BaseModel):
    status: str = Field(..., description="Authentication status: success or invalid_credentials")
    message: str = Field(..., description="Status message")
    username: Optional[str] = Field(None, description="Username if successful")
    risk_score: Optional[float] = Field(None, description="Risk score from ML model")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")

# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 60)
    print("Starting ZT-Verify Backend...")
    print("=" * 60)
    init_db()
    load_models()
    print("Backend ready!")
    yield
    # Shutdown
    print("Shutting down ZT-Verify Backend...")
    close_db()

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="ZT-Verify API",
    description="Zero-Trust Verification Backend with ML-based Risk Assessment",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow localhost:3000 and localhost:3001
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns the API health status
    """
    return {"status": "ok"}

@app.post("/api/authenticate", response_model=AuthenticateResponse, tags=["Authentication"])
async def authenticate(request: AuthenticateRequest):
    """
    Authenticate a user with username and password
    
    This endpoint:
    1. Validates user credentials using bcrypt
    2. Logs the login attempt
    3. Returns success or invalid_credentials status
    
    Args:
        request: Authentication request with credentials and device info
    
    Returns:
        Authentication response with status and optional risk score
    """
    try:
        # Get user from database
        user = get_user(request.username)
        
        if not user:
            # Log failed attempt - user not found
            log_login_attempt(
                username=request.username,
                ip_address=request.ip_address,
                device_fingerprint=request.device_fingerprint,
                location=request.location,
                risk_score=None,
                action="deny",
                success=False
            )
            
            return AuthenticateResponse(
                status="invalid_credentials",
                message="Invalid username or password"
            )
        
        # Check if user account is active
        if user['status'] != 'active':
            log_login_attempt(
                username=request.username,
                ip_address=request.ip_address,
                device_fingerprint=request.device_fingerprint,
                location=request.location,
                risk_score=None,
                action="deny",
                success=False
            )
            
            return AuthenticateResponse(
                status="invalid_credentials",
                message=f"Account is {user['status']}"
            )
        
        # Verify password with bcrypt
        password_match = bcrypt.checkpw(
            request.password.encode('utf-8'),
            user['password_hash'].encode('utf-8')
        )
        
        if not password_match:
            # Log failed attempt - wrong password
            log_login_attempt(
                username=request.username,
                ip_address=request.ip_address,
                device_fingerprint=request.device_fingerprint,
                location=request.location,
                risk_score=None,
                action="deny",
                success=False
            )
            
            return AuthenticateResponse(
                status="invalid_credentials",
                message="Invalid username or password"
            )
        
        # Password is correct - check device trust
        device_known = is_known_device(request.username, request.device_fingerprint)
        
        # Calculate risk score (simple version - can be enhanced with ML)
        risk_score = 0.0 if device_known else 0.5
        
        # Register/update device
        register_device(request.username, request.device_fingerprint)
        
        # Log successful attempt
        log_login_attempt(
            username=request.username,
            ip_address=request.ip_address,
            device_fingerprint=request.device_fingerprint,
            location=request.location,
            risk_score=risk_score,
            action="allow",
            success=True
        )
        
        return AuthenticateResponse(
            status="success",
            message="Authentication successful",
            username=request.username,
            risk_score=risk_score
        )
        
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during authentication")

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "ZT-Verify API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
