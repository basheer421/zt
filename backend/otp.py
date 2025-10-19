"""
OTP (One-Time Password) module for ZT-Verify
Handles OTP generation, email sending via Resend API, and verification
"""

import os
import random
import string
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import resend

from database import store_otp, verify_otp as db_verify_otp, get_active_otp

# Load environment variables from .env file
load_dotenv()

# Configure Resend API
resend.api_key = os.getenv("RESEND_API_KEY", "")

# Configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 3
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
APP_NAME = os.getenv("APP_NAME", "ZT-Verify")

# ============================================================================
# OTP GENERATION
# ============================================================================

def generate_otp(length: int = OTP_LENGTH) -> str:
    """
    Generate a random numeric OTP code
    
    Args:
        length: Length of OTP code (default: 6)
    
    Returns:
        String containing random digits
    
    Example:
        >>> otp = generate_otp()
        >>> len(otp)
        6
        >>> otp.isdigit()
        True
    """
    return ''.join(random.choices(string.digits, k=length))

# ============================================================================
# EMAIL SENDING
# ============================================================================

def send_otp_email(user_email: str, otp_code: str, username: str = "") -> Dict[str, Any]:
    """
    Send OTP code via email using Resend API
    
    Args:
        user_email: Recipient email address
        otp_code: OTP code to send
        username: Username (optional, for personalization)
    
    Returns:
        Dict with 'success' boolean and 'message' or 'error' string
    
    Raises:
        Exception if Resend API key is not configured
    """
    if not resend.api_key:
        return {
            'success': False,
            'error': 'Resend API key not configured'
        }
    
    try:
        # Prepare email content
        subject = f"Your {APP_NAME} Verification Code"
        
        username_greeting = f" {username}" if username else ""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🔐 {APP_NAME}</h1>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0;">
                <h2 style="color: #333; margin-top: 0;">Hello{username_greeting},</h2>
                
                <p style="font-size: 16px; color: #555;">
                    Your verification code is:
                </p>
                
                <div style="background: white; border: 2px dashed #667eea; border-radius: 8px; padding: 20px; text-align: center; margin: 25px 0;">
                    <p style="font-size: 36px; font-weight: bold; color: #667eea; letter-spacing: 8px; margin: 0; font-family: 'Courier New', monospace;">
                        {otp_code}
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 25px;">
                    <strong>⏱️ This code will expire in {OTP_EXPIRY_MINUTES} minutes.</strong>
                </p>
                
                <p style="font-size: 14px; color: #666;">
                    If you didn't request this code, please ignore this email or contact support if you're concerned about your account security.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 25px 0;">
                
                <p style="font-size: 12px; color: #999; text-align: center; margin-bottom: 0;">
                    This is an automated message from {APP_NAME}. Please do not reply to this email.
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #999; font-size: 12px;">
                <p>© 2025 {APP_NAME}. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        {APP_NAME} - Verification Code
        
        Hello{username_greeting},
        
        Your verification code is: {otp_code}
        
        This code will expire in {OTP_EXPIRY_MINUTES} minutes.
        
        If you didn't request this code, please ignore this email.
        
        ---
        This is an automated message from {APP_NAME}.
        © 2025 {APP_NAME}. All rights reserved.
        """
        
        # Send email via Resend
        params = {
            "from": FROM_EMAIL,
            "to": [user_email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }
        
        response = resend.Emails.send(params)
        
        return {
            'success': True,
            'message': 'OTP email sent successfully',
            'email_id': response.get('id', '')
        }
        
    except Exception as e:
        error_message = str(e)
        print(f"Error sending OTP email: {error_message}")
        
        return {
            'success': False,
            'error': f'Failed to send email: {error_message}'
        }

# ============================================================================
# OTP CHALLENGE CREATION
# ============================================================================

def create_otp_challenge(username: str, user_email: str) -> Dict[str, Any]:
    """
    Create and send an OTP challenge
    
    This function:
    1. Generates a new OTP code
    2. Stores it in the database with expiry time
    3. Sends it via email to the user
    
    Args:
        username: Username for the OTP challenge
        user_email: Email address to send OTP to
    
    Returns:
        Dict with 'success' boolean, 'message' string, and optional 'otp_id'
    
    Example:
        >>> result = create_otp_challenge("john_doe", "john@example.com")
        >>> result['success']
        True
    """
    try:
        # Check if there's an active OTP
        active_otp = get_active_otp(username)
        if active_otp:
            # Calculate remaining time
            expires_at = datetime.fromisoformat(active_otp['expires_at'])
            remaining_seconds = (expires_at - datetime.now()).total_seconds()
            
            if remaining_seconds > 0:
                return {
                    'success': False,
                    'error': f'An OTP was recently sent. Please wait {int(remaining_seconds)} seconds before requesting a new one.',
                    'remaining_seconds': int(remaining_seconds)
                }
        
        # Generate new OTP
        otp_code = generate_otp()
        
        # Store in database
        otp_id = store_otp(
            username=username,
            code=otp_code,
            expires_in_minutes=OTP_EXPIRY_MINUTES
        )
        
        # Send via email
        email_result = send_otp_email(
            user_email=user_email,
            otp_code=otp_code,
            username=username
        )
        
        if not email_result['success']:
            return {
                'success': False,
                'error': email_result.get('error', 'Failed to send email')
            }
        
        return {
            'success': True,
            'message': f'OTP sent to {user_email}',
            'otp_id': otp_id,
            'expires_in_minutes': OTP_EXPIRY_MINUTES,
            'email_id': email_result.get('email_id', '')
        }
        
    except Exception as e:
        error_message = str(e)
        print(f"Error creating OTP challenge: {error_message}")
        
        return {
            'success': False,
            'error': f'Failed to create OTP challenge: {error_message}'
        }

# ============================================================================
# OTP VERIFICATION
# ============================================================================

def verify_otp(username: str, entered_otp: str) -> Dict[str, Any]:
    """
    Verify an OTP code entered by the user
    
    This function:
    1. Validates the OTP against the database
    2. Checks if OTP has expired
    3. Tracks verification attempts (max 3)
    4. Marks OTP as verified if successful
    
    Args:
        username: Username to verify OTP for
        entered_otp: OTP code entered by the user
    
    Returns:
        Dict with:
        - 'valid': boolean indicating if OTP is valid
        - 'message': descriptive message
        - 'attempts_remaining': number of attempts left (if applicable)
    
    Example:
        >>> result = verify_otp("john_doe", "123456")
        >>> if result['valid']:
        ...     print("OTP verified successfully!")
    """
    try:
        # Strip whitespace from entered OTP
        entered_otp = entered_otp.strip()
        
        # Validate format
        if not entered_otp.isdigit() or len(entered_otp) != OTP_LENGTH:
            return {
                'valid': False,
                'message': f'Invalid OTP format. Must be {OTP_LENGTH} digits.',
                'attempts_remaining': None
            }
        
        # Verify using database function
        result = db_verify_otp(username, entered_otp)
        
        # Get active OTP to check attempts
        active_otp = get_active_otp(username)
        
        if result['valid']:
            return {
                'valid': True,
                'message': 'OTP verified successfully',
                'attempts_remaining': None
            }
        else:
            # Calculate remaining attempts
            attempts_remaining = None
            if active_otp and not active_otp['verified']:
                attempts_remaining = MAX_OTP_ATTEMPTS - active_otp['attempts']
            
            response = {
                'valid': False,
                'message': result['message'],
                'attempts_remaining': attempts_remaining
            }
            
            # Add specific messaging
            if 'expired' in result['message'].lower():
                response['message'] = 'OTP has expired. Please request a new one.'
            elif 'too many attempts' in result['message'].lower():
                response['message'] = 'Too many failed attempts. Please request a new OTP.'
            elif 'invalid' in result['message'].lower() and attempts_remaining:
                response['message'] = f'Invalid OTP code. {attempts_remaining} attempts remaining.'
            
            return response
        
    except Exception as e:
        error_message = str(e)
        print(f"Error verifying OTP: {error_message}")
        
        return {
            'valid': False,
            'message': 'An error occurred during OTP verification',
            'error': error_message,
            'attempts_remaining': None
        }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_otp_status(username: str) -> Dict[str, Any]:
    """
    Get the status of active OTP for a user
    
    Args:
        username: Username to check OTP status for
    
    Returns:
        Dict with OTP status information or None if no active OTP
    """
    try:
        active_otp = get_active_otp(username)
        
        if not active_otp:
            return {
                'has_active_otp': False,
                'message': 'No active OTP found'
            }
        
        expires_at = datetime.fromisoformat(active_otp['expires_at'])
        remaining_seconds = max(0, (expires_at - datetime.now()).total_seconds())
        
        return {
            'has_active_otp': True,
            'created_at': active_otp['created_at'],
            'expires_at': active_otp['expires_at'],
            'remaining_seconds': int(remaining_seconds),
            'attempts': active_otp['attempts'],
            'attempts_remaining': MAX_OTP_ATTEMPTS - active_otp['attempts'],
            'verified': bool(active_otp['verified'])
        }
        
    except Exception as e:
        print(f"Error getting OTP status: {str(e)}")
        return {
            'has_active_otp': False,
            'error': str(e)
        }

def format_remaining_time(seconds: int) -> str:
    """
    Format remaining time in a human-readable way
    
    Args:
        seconds: Number of seconds
    
    Returns:
        Formatted string like "2 minutes 30 seconds"
    """
    if seconds < 60:
        return f"{seconds} seconds"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if remaining_seconds > 0:
        return f"{minutes} minutes {remaining_seconds} seconds"
    else:
        return f"{minutes} minutes"
