#!/usr/bin/env python3
"""
Seed data generator for ZT-Verify system
Generates realistic training data for 5 users with varied patterns
"""

import random
import bcrypt
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import hashlib

from database import (
    init_db,
    create_user,
    log_login_attempt,
    register_device,
    get_user
)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Default password for all test users
DEFAULT_PASSWORD = "Test123!"

# Date range for historical data (30 days)
DAYS_OF_HISTORY = 30
ATTEMPTS_PER_USER = 300

# User agent strings for different devices
USER_AGENTS = {
    "chrome_windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "chrome_mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "firefox_linux": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "safari_iphone": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "edge_windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "chrome_android": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
}

# IP address ranges by location
IP_RANGES = {
    "New York": ["162.241.{}.{}", "192.168.1.{}"],
    "California": ["172.56.{}.{}", "10.0.0.{}"],
    "London": ["185.94.{}.{}", "192.168.10.{}"],
    "Tokyo": ["103.79.{}.{}", "192.168.20.{}"],
    "Sydney": ["103.28.{}.{}", "192.168.30.{}"],
    "Remote": ["203.0.113.{}", "198.51.100.{}"],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_device_fingerprint(user_agent: str) -> str:
    """Generate a device fingerprint from user agent"""
    return hashlib.sha256(user_agent.encode()).hexdigest()[:32]

def generate_ip_address(location: str) -> str:
    """Generate a random IP address for a location"""
    ip_template = random.choice(IP_RANGES[location])
    if ip_template.count('{}') == 2:
        return ip_template.format(random.randint(1, 254), random.randint(1, 254))
    else:
        return ip_template.format(random.randint(100, 199))

def generate_timestamp(
    base_date: datetime,
    hour_range: Tuple[int, int],
    weekdays_only: bool = False,
    variation_percent: float = 0.02
) -> datetime:
    """
    Generate a timestamp with realistic patterns
    
    Args:
        base_date: Base date for the timestamp
        hour_range: Tuple of (start_hour, end_hour) for typical activity
        weekdays_only: Whether to restrict to weekdays
        variation_percent: Percentage of times to violate the pattern
    """
    # Random variation - sometimes break the pattern
    if random.random() < variation_percent:
        # Anomaly: random time
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
    else:
        # Normal pattern
        hour = random.randint(hour_range[0], hour_range[1])
        minute = random.randint(0, 59)
    
    timestamp = base_date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
    
    # If weekdays only, skip weekends (unless it's a variation)
    if weekdays_only and timestamp.weekday() >= 5 and random.random() > variation_percent:
        # Move to next Monday
        days_until_monday = 7 - timestamp.weekday()
        timestamp += timedelta(days=days_until_monday)
    
    return timestamp

def calculate_risk_score(
    is_known_device: bool,
    is_typical_time: bool,
    is_typical_location: bool
) -> float:
    """Calculate risk score based on factors"""
    score = 0.0
    
    if not is_known_device:
        score += 0.4
    
    if not is_typical_time:
        score += 0.3
    
    if not is_typical_location:
        score += 0.3
    
    return min(score, 1.0)

# ============================================================================
# USER PROFILE CLASSES
# ============================================================================

class UserProfile:
    """Base class for user profiles"""
    
    def __init__(self, username: str, email: str, full_name: str):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.password_hash = hash_password(DEFAULT_PASSWORD)
        self.devices = []
        self.primary_location = "New York"
        self.typical_hours = (9, 17)  # 9 AM - 5 PM
        self.weekdays_only = True
    
    def get_devices(self) -> List[Dict]:
        """Get list of devices for this user"""
        return self.devices
    
    def generate_login_attempt(self, timestamp: datetime) -> Dict:
        """Generate a single login attempt"""
        # Choose device (favor first device if multiple)
        if len(self.devices) == 1:
            device = self.devices[0]
        else:
            device_weights = [0.7] + [0.3 / (len(self.devices) - 1)] * (len(self.devices) - 1)
            device = random.choices(self.devices, weights=device_weights)[0]
        
        # Determine if this is during typical hours
        is_typical_time = self.typical_hours[0] <= timestamp.hour <= self.typical_hours[1]
        
        # Choose location (98% primary, 2% other)
        if random.random() < 0.98:
            location = self.primary_location
            is_typical_location = True
        else:
            location = random.choice(list(IP_RANGES.keys()))
            is_typical_location = False
        
        # Generate IP for location
        ip_address = generate_ip_address(location)
        
        # Calculate risk score
        is_known_device = True  # All devices are registered
        risk_score = calculate_risk_score(is_known_device, is_typical_time, is_typical_location)
        
        # Determine success (higher risk = more likely to fail)
        success = risk_score < 0.5 or random.random() < 0.95
        action = "allow" if success else "challenge"
        
        return {
            "username": self.username,
            "timestamp": timestamp,
            "ip_address": ip_address,
            "device_fingerprint": device["fingerprint"],
            "location": location,
            "risk_score": risk_score,
            "action": action,
            "success": success
        }

class JohnDoeProfile(UserProfile):
    """Regular office worker - predictable schedule"""
    
    def __init__(self):
        super().__init__(
            username="john_doe",
            email="john.doe@example.com",
            full_name="John Doe"
        )
        self.devices = [
            {
                "name": "Work Laptop",
                "user_agent": USER_AGENTS["chrome_windows"],
                "fingerprint": generate_device_fingerprint(USER_AGENTS["chrome_windows"] + "_john")
            }
        ]
        self.primary_location = "New York"
        self.typical_hours = (9, 17)  # 9 AM - 5 PM
        self.weekdays_only = True

class JaneSmithProfile(UserProfile):
    """Shift worker - extended hours, works weekends"""
    
    def __init__(self):
        super().__init__(
            username="jane_smith",
            email="jane.smith@example.com",
            full_name="Jane Smith"
        )
        self.devices = [
            {
                "name": "Work Desktop",
                "user_agent": USER_AGENTS["chrome_mac"],
                "fingerprint": generate_device_fingerprint(USER_AGENTS["chrome_mac"] + "_jane")
            },
            {
                "name": "Personal Laptop",
                "user_agent": USER_AGENTS["firefox_linux"],
                "fingerprint": generate_device_fingerprint(USER_AGENTS["firefox_linux"] + "_jane")
            }
        ]
        self.primary_location = "California"
        self.typical_hours = (10, 22)  # 10 AM - 10 PM
        self.weekdays_only = False

class BobJonesProfile(UserProfile):
    """Traveler - irregular schedule, multiple locations"""
    
    def __init__(self):
        super().__init__(
            username="bob_jones",
            email="bob.jones@example.com",
            full_name="Bob Jones"
        )
        self.devices = [
            {
                "name": "Work Laptop",
                "user_agent": USER_AGENTS["chrome_windows"],
                "fingerprint": generate_device_fingerprint(USER_AGENTS["chrome_windows"] + "_bob")
            },
            {
                "name": "Personal Phone",
                "user_agent": USER_AGENTS["safari_iphone"],
                "fingerprint": generate_device_fingerprint(USER_AGENTS["safari_iphone"] + "_bob")
            },
            {
                "name": "Tablet",
                "user_agent": USER_AGENTS["chrome_android"],
                "fingerprint": generate_device_fingerprint(USER_AGENTS["chrome_android"] + "_bob")
            }
        ]
        self.primary_location = "Remote"  # No fixed location
        self.typical_hours = (0, 23)  # Any time
        self.weekdays_only = False
    
    def generate_login_attempt(self, timestamp: datetime) -> Dict:
        """Override to add more location variety"""
        attempt = super().generate_login_attempt(timestamp)
        # Bob travels - 40% chance of different location each time
        if random.random() < 0.4:
            attempt["location"] = random.choice(["London", "Tokyo", "Sydney", "New York", "California"])
            attempt["ip_address"] = generate_ip_address(attempt["location"])
            attempt["risk_score"] = min(attempt["risk_score"] + 0.2, 1.0)
        return attempt

class AliceAdminProfile(UserProfile):
    """Admin user - random patterns, any time"""
    
    def __init__(self):
        super().__init__(
            username="alice_admin",
            email="alice.admin@example.com",
            full_name="Alice Admin"
        )
        self.devices = [
            {
                "name": "Admin Workstation",
                "user_agent": USER_AGENTS["edge_windows"],
                "fingerprint": generate_device_fingerprint(USER_AGENTS["edge_windows"] + "_alice")
            }
        ]
        self.primary_location = "New York"
        self.typical_hours = (0, 23)  # Any time
        self.weekdays_only = False

class TestUserProfile(UserProfile):
    """Test user - for generating anomalies"""
    
    def __init__(self):
        super().__init__(
            username="test_user",
            email="test.user@example.com",
            full_name="Test User"
        )
        self.devices = [
            {
                "name": "Test Device",
                "user_agent": USER_AGENTS["chrome_windows"],
                "fingerprint": generate_device_fingerprint(USER_AGENTS["chrome_windows"] + "_test")
            }
        ]
        self.primary_location = "New York"
        self.typical_hours = (9, 17)
        self.weekdays_only = True
    
    def generate_login_attempt(self, timestamp: datetime) -> Dict:
        """Override to generate more anomalies (20% instead of 2%)"""
        attempt = super().generate_login_attempt(timestamp)
        
        # 20% anomalies for test user
        if random.random() < 0.2:
            attempt["location"] = random.choice(list(IP_RANGES.keys()))
            attempt["ip_address"] = generate_ip_address(attempt["location"])
            attempt["risk_score"] = random.uniform(0.6, 1.0)
            attempt["action"] = "challenge" if attempt["risk_score"] > 0.7 else "allow"
            attempt["success"] = random.random() < 0.5
        
        return attempt

# ============================================================================
# SEED FUNCTIONS
# ============================================================================

def create_users() -> List[UserProfile]:
    """Create all user profiles"""
    profiles = [
        JohnDoeProfile(),
        JaneSmithProfile(),
        BobJonesProfile(),
        AliceAdminProfile(),
        TestUserProfile()
    ]
    
    print("Creating users...")
    for profile in profiles:
        # Check if user already exists
        existing_user = get_user(profile.username)
        if existing_user:
            print(f"  ⚠ User {profile.username} already exists, skipping creation")
        else:
            user_id = create_user(
                username=profile.username,
                password_hash=profile.password_hash,
                email=profile.email,
                status="active"
            )
            print(f"  ✓ Created user: {profile.username} (ID: {user_id})")
    
    return profiles

def register_user_devices(profiles: List[UserProfile]):
    """Register all devices for users"""
    print("\nRegistering devices...")
    for profile in profiles:
        for device in profile.devices:
            device_id = register_device(profile.username, device["fingerprint"])
            print(f"  ✓ Registered device '{device['name']}' for {profile.username}")

def generate_login_history(profiles: List[UserProfile]):
    """Generate historical login attempts for all users"""
    print(f"\nGenerating {ATTEMPTS_PER_USER} login attempts per user over {DAYS_OF_HISTORY} days...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_OF_HISTORY)
    
    total_attempts = 0
    
    for profile in profiles:
        print(f"\n  Processing {profile.username}...")
        
        # Generate timestamps spread over the date range
        timestamps = []
        for i in range(ATTEMPTS_PER_USER):
            # Spread attempts across the date range
            day_offset = random.randint(0, DAYS_OF_HISTORY - 1)
            base_date = start_date + timedelta(days=day_offset)
            
            # Generate timestamp with user's pattern
            timestamp = generate_timestamp(
                base_date,
                profile.typical_hours,
                profile.weekdays_only,
                variation_percent=0.02
            )
            timestamps.append(timestamp)
        
        # Sort timestamps chronologically
        timestamps.sort()
        
        # Generate and log attempts
        successful = 0
        challenged = 0
        denied = 0
        
        for timestamp in timestamps:
            attempt = profile.generate_login_attempt(timestamp)
            
            log_login_attempt(
                username=attempt["username"],
                ip_address=attempt["ip_address"],
                device_fingerprint=attempt["device_fingerprint"],
                location=attempt["location"],
                risk_score=attempt["risk_score"],
                action=attempt["action"],
                success=attempt["success"]
            )
            
            if attempt["success"]:
                successful += 1
            elif attempt["action"] == "challenge":
                challenged += 1
            else:
                denied += 1
            
            total_attempts += 1
        
        print(f"    ✓ Generated {ATTEMPTS_PER_USER} attempts")
        print(f"      Successful: {successful}, Challenged: {challenged}, Denied: {denied}")
        print(f"      Success rate: {successful/ATTEMPTS_PER_USER*100:.1f}%")
    
    print(f"\n  Total login attempts generated: {total_attempts}")

def print_statistics():
    """Print database statistics"""
    from database import get_login_stats, list_all_users, execute_query
    
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    
    # User count
    users = list_all_users()
    print(f"\nTotal Users: {len(users)}")
    for user in users:
        print(f"  - {user['username']} ({user['email']}) - {user['status']}")
    
    # Login stats
    stats = get_login_stats(days=DAYS_OF_HISTORY)
    print(f"\nLogin Statistics (last {DAYS_OF_HISTORY} days):")
    print(f"  Total attempts: {stats.get('total_attempts', 0)}")
    print(f"  Successful: {stats.get('successful_logins', 0)}")
    print(f"  Failed: {stats.get('failed_logins', 0)}")
    print(f"  Success rate: {stats.get('successful_logins', 0) / max(stats.get('total_attempts', 1), 1) * 100:.1f}%")
    print(f"  Unique users: {stats.get('unique_users', 0)}")
    print(f"  Average risk score: {stats.get('avg_risk_score', 0):.3f}")
    
    # Device count
    device_query = "SELECT COUNT(*) as count FROM user_devices"
    device_result = execute_query(device_query)
    print(f"\nTotal Registered Devices: {device_result[0]['count']}")
    
    # Per-user statistics
    print(f"\nPer-User Statistics:")
    for user in users:
        user_query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                AVG(risk_score) as avg_risk
            FROM login_attempts
            WHERE username = ?
        """
        user_stats = execute_query(user_query, (user['username'],))[0]
        
        # Skip users with no attempts
        if user_stats['total'] == 0:
            continue
            
        print(f"  {user['username']}:")
        print(f"    Attempts: {user_stats['total']}")
        successful = user_stats['successful'] if user_stats['successful'] is not None else 0
        print(f"    Success rate: {successful / max(user_stats['total'], 1) * 100:.1f}%")
        avg_risk = user_stats['avg_risk'] if user_stats['avg_risk'] is not None else 0.0
        print(f"    Avg risk score: {avg_risk:.3f}")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def seed_database():
    """Main function to seed the database with training data"""
    print("=" * 60)
    print("ZT-VERIFY DATABASE SEEDING")
    print("=" * 60)
    print(f"\nGenerating {ATTEMPTS_PER_USER} login attempts per user")
    print(f"Date range: {DAYS_OF_HISTORY} days")
    print(f"Default password for all users: {DEFAULT_PASSWORD}")
    print("\n" + "=" * 60)
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Create users
    profiles = create_users()
    
    # Register devices
    register_user_devices(profiles)
    
    # Generate login history
    generate_login_history(profiles)
    
    # Print statistics
    print_statistics()
    
    print("\n" + "=" * 60)
    print("✓ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nYou can now use this data for training ML models.")
    print("All users have the same password: Test123!")
    print("\nUser profiles:")
    print("  1. john_doe - Regular 9-5 worker (New York, 1 device)")
    print("  2. jane_smith - Shift worker 10AM-10PM (California, 2 devices)")
    print("  3. bob_jones - Frequent traveler (Multiple locations, 3 devices)")
    print("  4. alice_admin - Admin with random patterns (New York, 1 device)")
    print("  5. test_user - Test account with anomalies (New York, 1 device)")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    seed_database()
