"""
UAE-Focused Risk Assessment with Hybrid ML + Rules
Combines trained ML model with practical rules for UAE deployment
"""

from typing import Dict, Any
import joblib
from pathlib import Path
import pandas as pd
import ipaddress
from datetime import datetime

# Load trained model
MODELS_DIR = Path(__file__).parent / "models"
GLOBAL_MODEL_PATH = MODELS_DIR / "global_model.pkl"

_global_model = None

def get_global_model():
    global _global_model
    if _global_model is None:
        try:
            _global_model = joblib.load(GLOBAL_MODEL_PATH)
        except:
            pass
    return _global_model

# UAE-specific configuration
UAE_GULF_COUNTRIES = ['AE', 'SA', 'QA', 'KW', 'OM', 'BH']
REGIONAL_SAFE = ['JO', 'LB', 'EG']
ACCEPTABLE_COUNTRIES = ['US', 'GB', 'DE', 'FR', 'SG', 'AU', 'IN']  # Business partners
HIGH_RISK_COUNTRIES = ['RU', 'CN', 'KP', 'NG', 'RO', 'UA', 'BR']

# UAE ISPs
UAE_ASNS = [5384, 15802, 42298, 35753, 36351]  # Etisalat, Du, etc.

# Known attack ASNs from dataset
ATTACK_ASNS = [3280, 503109, 62350, 56851]

# Cloud provider ASNs (AWS, Azure, GCP, DigitalOcean, etc.) - potential VPN/proxy
CLOUD_ASNS = [16509, 14618, 15169, 8075, 14061, 396982]  # AWS, Amazon, Google, Microsoft, DigitalOcean

# Business hours in UAE (UTC+4, so 04:00-14:00 UTC is 8 AM - 6 PM local)
BUSINESS_HOURS_UTC = list(range(4, 15))  # 8 AM - 6 PM UAE time
SUSPICIOUS_HOURS_UTC = list(range(22, 24)) + list(range(0, 3))  # 2 AM - 6 AM UAE time

def is_private_ip(ip_str: str) -> bool:
    """Check if IP is in private range"""
    try:
        ip = ipaddress.IPv4Address(ip_str)
        return ip.is_private
    except:
        return False

def is_cloud_ip(ip_str: str) -> bool:
    """Check if IP is likely from a cloud provider (basic check)"""
    try:
        ip = ipaddress.IPv4Address(ip_str)
        # Common cloud provider ranges (simplified)
        cloud_ranges = [
            ipaddress.IPv4Network('3.0.0.0/8'),      # AWS
            ipaddress.IPv4Network('13.0.0.0/8'),     # AWS
            ipaddress.IPv4Network('52.0.0.0/8'),     # AWS
            ipaddress.IPv4Network('104.0.0.0/8'),    # Azure
            ipaddress.IPv4Network('35.0.0.0/8'),     # GCP
        ]
        return any(ip in network for network in cloud_ranges)
    except:
        return False

def extract_features(login_data: Dict[str, Any]) -> pd.DataFrame:
    """Extract features for ML model"""
    try:
        timestamp = pd.to_datetime(login_data.get('timestamp', datetime.utcnow()))
        login_hour = timestamp.hour
        
        ip_str = login_data.get('ip_address', '0.0.0.0')
        try:
            ip_int = int(ipaddress.IPv4Address(ip_str))
        except:
            ip_int = 0
        
        features = {
            'ASN': login_data.get('asn', 0),
            'Login Hour': login_hour,
            'IP Address': ip_int,
            'User Agent String': hash(login_data.get('user_agent', '')) % 10000,
            'Browser Name and Version': hash(login_data.get('browser', '')) % 10000,
            'OS Name and Version': hash(login_data.get('os', '')) % 10000,
            'Country': login_data.get('country', 'XX'),
            'Device Type': login_data.get('device_type', 'desktop')
        }
        return pd.DataFrame([features])
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None

def assess_risk_rules(username: str, login_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rule-based risk assessment for UAE deployment
    Returns risk score 0-100 and explanation
    """
    risk_score = 0
    risk_factors = []
    
    country = login_data.get('country', 'XX')
    asn = login_data.get('asn', 0)
    ip = login_data.get('ip_address', '0.0.0.0')
    user_agent = login_data.get('user_agent', '').lower()
    device_type = login_data.get('device_type', 'desktop')
    
    # Parse timestamp
    try:
        timestamp = pd.to_datetime(login_data.get('timestamp', datetime.utcnow()))
        hour_utc = timestamp.hour
    except:
        hour_utc = 12
    
    # Check for bots/automation FIRST (before country checks)
    is_bot = any(bot in user_agent for bot in ['python', 'curl', 'wget', 'bot', 'headless', 'phantom'])
    
    # === GREEN CASES (LOW RISK 0-25%) ===
    
    # UAE/Gulf countries with UAE ISPs = Very Safe (but check for bots)
    if country in UAE_GULF_COUNTRIES and asn in UAE_ASNS:
        risk_score = 5
        risk_factors.append(f"✓ UAE/Gulf country ({country}) with local ISP")
        
        # Even UAE logins get flagged if automated
        if is_bot:
            risk_score = 75
            risk_factors.append(f"🚨 Automated/bot user agent")
            return {
                'risk_score': risk_score,
                'risk_level': 'high',
                'risk_factors': risk_factors,
                'is_anomaly': True,
                'method': 'rules'
            }
        
        return {
            'risk_score': risk_score,
            'risk_level': 'low',
            'risk_factors': risk_factors,
            'is_anomaly': False,
            'method': 'rules'
        }
    
    # UAE/Gulf countries = Safe (but check for bots)
    if country in UAE_GULF_COUNTRIES:
        risk_score = 10
        risk_factors.append(f"✓ UAE/Gulf country ({country})")
        
        # Bot check
        if is_bot:
            risk_score = 70
            risk_factors.append(f"🚨 Automated/bot user agent from UAE")
            return {
                'risk_score': risk_score,
                'risk_level': 'high',
                'risk_factors': risk_factors,
                'is_anomaly': True,
                'method': 'rules'
            }
        
        # Bonus for business hours
        if hour_utc in BUSINESS_HOURS_UTC:
            risk_score -= 5
            risk_factors.append("✓ Business hours")
        
        return {
            'risk_score': max(0, risk_score),
            'risk_level': 'low',
            'risk_factors': risk_factors,
            'is_anomaly': False,
            'method': 'rules'
        }
    
    # === YELLOW CASES (MEDIUM RISK 30-65%) ===
    
    # Regional safe countries
    if country in REGIONAL_SAFE:
        risk_score = 35
        risk_factors.append(f"⚠️  Regional country ({country})")
    
    # Acceptable business countries
    elif country in ACCEPTABLE_COUNTRIES:
        risk_score = 40
        risk_factors.append(f"⚠️  Acceptable country ({country})")

        # Check for cloud/VPN usage (increases risk)
        if asn in CLOUD_ASNS or is_cloud_ip(ip):
            risk_score += 10
            risk_factors.append("⚠️  Cloud provider IP (potential VPN)")

        # Reduce risk for India during business hours (outsourcing)
        if country == 'IN' and hour_utc in range(4, 14):  # 9:30 AM - 6:30 PM India time
            risk_score -= 10
            risk_factors.append("✓ India business hours")    # Unknown country = medium risk
    else:
        if country not in HIGH_RISK_COUNTRIES:
            risk_score = 45
            risk_factors.append(f"⚠️  Unfamiliar country ({country})")
    
    # === RED CASES (HIGH RISK 70-100%) ===
    
    # High-risk countries
    if country in HIGH_RISK_COUNTRIES:
        risk_score = 80
        risk_factors.append(f"🚨 High-risk country ({country})")
    
    # Private IP addresses (suspicious)
    if is_private_ip(ip):
        risk_score += 25
        risk_factors.append(f"🚨 Private IP address ({ip})")
    
    # Known attack ASNs from dataset
    if asn in ATTACK_ASNS:
        risk_score += 30
        risk_factors.append(f"🚨 Known malicious ASN ({asn})")
    
    # Bot/automated patterns (already checked for UAE above, but apply to others)
    if is_bot and country not in UAE_GULF_COUNTRIES:
        risk_score += 35
        risk_factors.append(f"🚨 Automated/bot user agent")
    
    # Suspicious hours (even in UAE)
    if hour_utc in SUSPICIOUS_HOURS_UTC and country in UAE_GULF_COUNTRIES:
        risk_score += 15
        risk_factors.append(f"⚠️  Suspicious hour (2-6 AM UAE time)")
    
    # Cap at 100
    risk_score = min(100, risk_score)
    
    # Determine risk level
    if risk_score < 30:
        risk_level = 'low'
        is_anomaly = False
    elif risk_score < 70:
        risk_level = 'medium'
        is_anomaly = False  # Require 2FA but not block
    else:
        risk_level = 'high'
        is_anomaly = True  # Block or strong verification
    
    return {
        'risk_score': risk_score,
        'risk_level': risk_level,
        'risk_factors': risk_factors,
        'is_anomaly': is_anomaly,
        'method': 'rules'
    }

def predict_risk_hybrid(username: str, login_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hybrid approach: Use rules + ML model
    """
    # Get rule-based assessment
    rules_result = assess_risk_rules(username, login_data)
    
    # Try ML model as secondary signal
    model = get_global_model()
    ml_score = None
    
    if model is not None:
        try:
            features_df = extract_features(login_data)
            if features_df is not None:
                probabilities = model.predict_proba(features_df)[0]
                ml_probability = probabilities[1]
                ml_score = int(ml_probability * 100)
        except Exception as e:
            print(f"ML prediction error: {e}")
    
    # Combine results: use rules as primary, ML as adjustment
    final_score = rules_result['risk_score']
    
    if ml_score is not None and ml_score > 50:
        # If ML also thinks it's risky, increase confidence
        final_score = min(100, final_score + 10)
        rules_result['risk_factors'].append(f"⚠️  ML model flagged (ML score: {ml_score}%)")
    
    rules_result['risk_score'] = final_score
    rules_result['ml_score'] = ml_score
    
    # Recalculate level and anomaly status
    if final_score < 30:
        rules_result['risk_level'] = 'low'
        rules_result['is_anomaly'] = False
    elif final_score < 70:
        rules_result['risk_level'] = 'medium'
        rules_result['is_anomaly'] = False
    else:
        rules_result['risk_level'] = 'high'
        rules_result['is_anomaly'] = True
    
    return rules_result

# Alias for compatibility with existing code
predict_risk = predict_risk_hybrid
