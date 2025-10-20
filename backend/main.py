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
from otp import create_otp_challenge, verify_otp as otp_verify, get_otp_status

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

class RequestOTPRequest(BaseModel):
    username: str = Field(..., description="Username to send OTP to")

class RequestOTPResponse(BaseModel):
    success: bool = Field(..., description="Whether OTP was sent successfully")
    message: str = Field(..., description="Status message")
    expires_in_minutes: Optional[int] = Field(None, description="OTP expiry time in minutes")

class VerifyOTPRequest(BaseModel):
    username: str = Field(..., description="Username")
    otp_code: str = Field(..., description="OTP code to verify")

class VerifyOTPResponse(BaseModel):
    valid: bool = Field(..., description="Whether OTP is valid")
    message: str = Field(..., description="Verification message")
    attempts_remaining: Optional[int] = Field(None, description="Number of attempts remaining")

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

# CORS middleware - Allow localhost ports for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",  # Vite default port
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
        
        # DECISION: Require 2FA for unknown devices or high-risk scenarios
        # You can customize this logic based on your requirements
        require_2fa = not device_known  # Require 2FA for unknown devices
        
        if require_2fa:
            # Return OTP challenge instead of allowing direct login
            log_login_attempt(
                username=request.username,
                ip_address=request.ip_address,
                device_fingerprint=request.device_fingerprint,
                location=request.location,
                risk_score=risk_score,
                action="challenge",
                success=False
            )
            
            return AuthenticateResponse(
                status="otp",
                message="Two-factor authentication required",
                username=request.username,
                risk_score=risk_score
            )
        
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
# OTP ENDPOINTS
# ============================================================================

@app.post("/api/otp/request", response_model=RequestOTPResponse, tags=["OTP"])
async def request_otp(request: RequestOTPRequest):
    """
    Request an OTP code to be sent to the user's email
    
    This endpoint:
    1. Validates that the user exists
    2. Generates a new OTP code
    3. Sends it via email
    4. Stores it in the database with 5-minute expiry
    
    Args:
        request: Request containing username
    
    Returns:
        Response indicating success/failure and expiry time
    """
    try:
        # Get user to validate and get email
        user = get_user(request.username)
        
        if not user:
            return RequestOTPResponse(
                success=False,
                message="User not found"
            )
        
        # Check if user account is active
        if user['status'] != 'active':
            return RequestOTPResponse(
                success=False,
                message=f"Account is {user['status']}"
            )
        
        # Create OTP challenge
        result = create_otp_challenge(request.username, user['email'])
        
        if result['success']:
            return RequestOTPResponse(
                success=True,
                message=result['message'],
                expires_in_minutes=result.get('expires_in_minutes')
            )
        else:
            return RequestOTPResponse(
                success=False,
                message=result.get('error', 'Failed to create OTP')
            )
        
    except Exception as e:
        print(f"OTP request error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during OTP request")

@app.post("/api/otp/verify", response_model=VerifyOTPResponse, tags=["OTP"])
async def verify_otp_endpoint(request: VerifyOTPRequest):
    """
    Verify an OTP code entered by the user
    
    This endpoint:
    1. Validates the OTP code against the database
    2. Checks if OTP has expired
    3. Tracks verification attempts (max 3)
    4. Marks OTP as verified if successful
    
    Args:
        request: Request containing username and OTP code
    
    Returns:
        Response indicating if OTP is valid and attempts remaining
    """
    try:
        # Verify OTP
        result = otp_verify(request.username, request.otp_code)
        
        return VerifyOTPResponse(
            valid=result['valid'],
            message=result['message'],
            attempts_remaining=result.get('attempts_remaining')
        )
        
    except Exception as e:
        print(f"OTP verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during OTP verification")

@app.get("/api/otp/status/{username}", tags=["OTP"])
async def get_otp_status_endpoint(username: str):
    """
    Get the status of active OTP for a user
    
    Args:
        username: Username to check OTP status for
    
    Returns:
        OTP status information including expiry and attempts
    """
    try:
        status = get_otp_status(username)
        return status
        
    except Exception as e:
        print(f"OTP status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while checking OTP status")

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
