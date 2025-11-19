from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import bcrypt
from datetime import datetime
import requests

from database import (
    init_db, 
    close_db,
    get_user,
    log_login_attempt,
    register_device,
    is_known_device
)
from ml_engine_uae import predict_risk_hybrid as predict_risk
from otp import create_otp_challenge, verify_otp as otp_verify, get_otp_status
from admin_routes import router as admin_router
from inventory_routes import router as inventory_router

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AuthenticateRequest(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    timestamp: str = Field(..., description="Login timestamp")
    device_fingerprint: str = Field(..., description="Unique device identifier")
    ip_address: Optional[str] = Field(None, description="Client IP address (auto-detected if not provided)")
    location: Optional[str] = Field(None, description="Geographic location (auto-detected if not provided)")
    user_agent: Optional[str] = Field(None, description="Browser user agent string")
    asn: Optional[int] = Field(None, description="Autonomous System Number for IP")

class AuthenticateResponse(BaseModel):
    status: str = Field(..., description="Authentication status: success or invalid_credentials")
    message: str = Field(..., description="Status message")
    username: Optional[str] = Field(None, description="Username if successful")
    risk_score: Optional[float] = Field(None, description="Risk score from ML model")
    role: Optional[str] = Field(None, description="User role (admin, manager, viewer)")

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
    print("✓ Database initialized")
    print("✓ UAE-focused ML engine ready")
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

# CORS middleware - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include admin routes
app.include_router(admin_router)

# Include inventory routes
app.include_router(inventory_router)

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
async def authenticate(auth_request: AuthenticateRequest, http_request: Request):
    """
    Authenticate a user with username and password
    
    This endpoint:
    1. Validates user credentials using bcrypt
    2. Logs the login attempt
    3. Returns success or invalid_credentials status
    
    Args:
        auth_request: Authentication request with credentials and device info
        http_request: FastAPI Request object for accessing headers
    
    Returns:
        Authentication response with status and optional risk score
    """
    try:
        # Auto-detect IP address from headers if not provided
        client_ip = auth_request.ip_address
        if not client_ip:
            # Try X-Forwarded-For first (for proxies/load balancers)
            client_ip = http_request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            # Fall back to X-Real-IP
            if not client_ip:
                client_ip = http_request.headers.get("X-Real-IP", "")
            # Fall back to direct client
            if not client_ip and http_request.client:
                client_ip = http_request.client.host
            # Default fallback
            if not client_ip:
                client_ip = "unknown"
        
        # Auto-detect location from IP if not provided
        location = auth_request.location
        if not location and client_ip and client_ip != "unknown":
            # Use IP geolocation service to detect real location
            try:
                # Using ip-api.com (free, no API key needed, 45 req/min limit)
                print(f"[GEO] Detecting location for IP: {client_ip}")
                geo_response = requests.get(f"http://ip-api.com/json/{client_ip}", timeout=2)        
                if geo_response.status_code == 200:
                    geo_data = geo_response.json()
                    print(f"[GEO] API Response: {geo_data}")
                    if geo_data.get('status') == 'success':
                        city = geo_data.get('city', 'Unknown')
                        country_code = geo_data.get('countryCode', 'XX')
                        location = f"{city}, {country_code}"
                        print(f"[GEO] Detected: {location}")
                    else:
                        location = "Unknown, XX"
                        print(f"[GEO] API returned failure status")
                else:
                    location = "Unknown, XX"
                    print(f"[GEO] API returned status code: {geo_response.status_code}")
            except Exception as e:
                print(f"[GEO] Geolocation error: {e}")
                location = "Unknown, XX"
        user = get_user(auth_request.username)
        
        if not user:
            # Log failed attempt - user not found
            log_login_attempt(
                username=auth_request.username,
                ip_address=client_ip,
                device_fingerprint=auth_request.device_fingerprint,
                location=location,
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
                username=auth_request.username,
                ip_address=client_ip,
                device_fingerprint=auth_request.device_fingerprint,
                location=location,
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
            auth_request.password.encode('utf-8'),
            user['password_hash'].encode('utf-8')
        )
        
        if not password_match:
            # Log failed attempt - wrong password
            log_login_attempt(
                username=auth_request.username,
                ip_address=client_ip,
                device_fingerprint=auth_request.device_fingerprint,
                location=location,
                risk_score=None,
                action="deny",
                success=False
            )
            
            return AuthenticateResponse(
                status="invalid_credentials",
                message="Invalid username or password"
            )
        
        # Password is correct - use ML to assess risk
        # Prepare login data for UAE ML engine
        # Parse location to get country (format: "City, Country" or "City, XX")
        country = 'XX'
        if location:
            parts = location.split(',')
            if len(parts) >= 2:
                country = parts[-1].strip()[:2].upper()
        
        # Debug logging
        print(f"[AUTH DEBUG] User: {auth_request.username}, IP: {client_ip}, Location: {location}, Country: {country}")
        
        login_data = {
            'ip_address': client_ip,
            'country': country,
            'asn': auth_request.asn or 0,  # Use provided ASN or default to 0
            'device_type': 'desktop',  # Could be enhanced with device fingerprint parsing
            'user_agent': auth_request.user_agent or 'Unknown',  # Use provided user agent
            'browser': 'Unknown',
            'os': 'Unknown',
            'timestamp': auth_request.timestamp
        }
        
        # HARDCODED DEMO USERS - Override ML predictions for demo purposes
        # These users always return specific risk levels regardless of actual data
        # HOWEVER: India location ALWAYS requires 2FA, even for demo users
        DEMO_USERS = {
            'green_user': 15,   # Low risk - GREEN (0-29)
            'yellow_user': 50,  # Medium risk - YELLOW (30-69)
            'red_user': 85      # High risk - RED (70-100)
        }

        # Check if login is from India FIRST (applies to all users including demos)
        # Also apply to test user 'india_user' for testing purposes
        if country == 'IN' or auth_request.username == 'india_user':
            # India always requires 2FA - set minimum risk to 40 (medium)
            ml_risk_score = 40
            risk_assessment = {
                'risk_score': 40,
                'risk_level': 'medium',
                'factors': ['India login - 2FA required by policy' if country == 'IN' else 'Test: India user - 2FA required']
            }
        elif auth_request.username in DEMO_USERS:
            # Use hardcoded risk score for demo users (only if not from India)
            ml_risk_score = DEMO_USERS[auth_request.username]
            risk_assessment = {
                'risk_score': ml_risk_score,
                'risk_level': 'low' if ml_risk_score < 30 else 'medium' if ml_risk_score < 70 else 'high',
                'factors': ['Demo user with hardcoded risk score']
            }
        else:
            # Get ML-based risk assessment for regular users
            risk_assessment = predict_risk(auth_request.username, login_data)
            ml_risk_score = risk_assessment['risk_score']  # Keep original 0-100 score
        
        risk_score = ml_risk_score / 100.0  # Convert 0-100 to 0-1 for compatibility

        # DECISION: Require 2FA based on ML risk assessment
        # High risk (70+) = Require 2FA
        # Medium risk (30-70) = Require 2FA for unknown devices
        # Low risk (<30) = Allow direct login
        # EXCEPTION: India logins ALWAYS require 2FA regardless of device
        device_known = is_known_device(auth_request.username, auth_request.device_fingerprint)       

        # Force 2FA for India logins (country == 'IN' or username == 'india_user')
        if country == 'IN' or auth_request.username == 'india_user':
            require_2fa = True
            print(f"[2FA] FORCING 2FA for India/india_user - Username: {auth_request.username}, Country: {country}")
        elif ml_risk_score >= 70:
            # High risk - always require 2FA
            require_2fa = True
            print(f"[2FA] High risk score ({ml_risk_score}) - Requiring 2FA")
        elif ml_risk_score >= 30:
            # Medium risk - require 2FA for unknown devices
            require_2fa = not device_known
            print(f"[2FA] Medium risk ({ml_risk_score}) - Device known: {device_known}, Require 2FA: {require_2fa}")
        else:
            # Low risk - allow direct login
            require_2fa = False
            print(f"[2FA] Low risk ({ml_risk_score}) - Allowing direct login")

        print(f"[2FA] FINAL DECISION - require_2fa: {require_2fa}")
        
        if require_2fa:
            # Return OTP challenge instead of allowing direct login
            print(f"[RESPONSE] Returning OTP challenge for user: {auth_request.username}")
            log_login_attempt(
                username=auth_request.username,
                ip_address=client_ip,
                device_fingerprint=auth_request.device_fingerprint,
                location=location,
                risk_score=risk_score,
                action="challenge",
                success=False
            )

            otp_response = AuthenticateResponse(
                status="otp",
                message="Two-factor authentication required",
                username=auth_request.username,
                risk_score=risk_score,
                role=user.get('role', 'viewer')
            )
            print(f"[RESPONSE] OTP Response: status={otp_response.status}, message={otp_response.message}")
            return otp_response
        
        # Register/update device
        register_device(auth_request.username, auth_request.device_fingerprint)
        
        # Log successful attempt
        log_login_attempt(
            username=auth_request.username,
            ip_address=client_ip,
            device_fingerprint=auth_request.device_fingerprint,
            location=location,
            risk_score=risk_score,
            action="allow",
            success=True
        )
        
        return AuthenticateResponse(
            status="success",
            message="Authentication successful",
            username=auth_request.username,
            risk_score=risk_score,
            role=user.get('role', 'viewer')  # Include user role in response
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
