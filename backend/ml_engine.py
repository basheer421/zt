"""
ML Engine for ZT-Verify
Handles feature extraction, model training, and risk prediction
"""

import os
import joblib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import numpy as np
from sklearn.svm import OneClassSVM
from dotenv import load_dotenv

from database import get_user_history, get_user_devices, is_known_device

# Load environment variables
load_dotenv()

# Model storage
MODELS_DIR = Path(__file__).parent / "models"
_loaded_models: Dict[str, Any] = {}

# ============================================================================
# DIRECTORY MANAGEMENT
# ============================================================================

def ensure_models_dir():
    """Ensure models directory exists"""
    MODELS_DIR.mkdir(exist_ok=True)
    print(f"Models directory: {MODELS_DIR}")

def load_models():
    """Load all .pkl models from the models directory"""
    ensure_models_dir()
    global _loaded_models
    
    print("Loading ML models...")
    model_files = list(MODELS_DIR.glob("*_model.pkl"))
    
    if not model_files:
        print("No user model files found in models directory")
        return
    
    for model_path in model_files:
        try:
            model_name = model_path.stem
            _loaded_models[model_name] = joblib.load(model_path)
            print(f"Loaded model: {model_name}")
        except Exception as e:
            print(f"Error loading model {model_path.name}: {e}")
    
    print(f"Total models loaded: {len(_loaded_models)}")

def get_model(model_name: str) -> Optional[Any]:
    """Get a loaded model by name"""
    return _loaded_models.get(model_name)

def list_available_models() -> List[str]:
    """List all available model names"""
    return list(_loaded_models.keys())

# ============================================================================
# FEATURE EXTRACTION
# ============================================================================

def calculate_device_similarity(device1: str, device2: str) -> float:
    """
    Calculate similarity between two device fingerprints
    
    Args:
        device1: First device fingerprint
        device2: Second device fingerprint
    
    Returns:
        Similarity score between 0 and 1
    """
    return SequenceMatcher(None, device1, device2).ratio()

def get_hours_since_last_login(username: str, current_timestamp: datetime) -> float:
    """
    Calculate hours since user's last login
    
    Args:
        username: Username to check
        current_timestamp: Current login timestamp
    
    Returns:
        Hours since last login, or 24.0 if no history
    """
    history = get_user_history(username, limit=1)
    
    if not history:
        return 24.0  # Default if no history
    
    last_login = history[0]
    last_timestamp = datetime.fromisoformat(last_login['timestamp'])
    
    hours_diff = (current_timestamp - last_timestamp).total_seconds() / 3600.0
    
    # Cap at 168 hours (7 days) to avoid extreme values
    return min(hours_diff, 168.0)

def extract_features(login_data: Dict[str, Any], user_history: List[Dict[str, Any]]) -> np.ndarray:
    """
    Extract features from login data for ML model
    
    Args:
        login_data: Dictionary containing:
            - timestamp: datetime or ISO string
            - device_fingerprint: str
            - location: str (optional)
            - username: str
        user_history: List of previous login attempts
    
    Returns:
        NumPy array with 6 features:
        [hour_of_day, day_of_week, device_similarity, is_known_device, 
         hours_since_last, is_known_location]
    """
    # Parse timestamp
    if isinstance(login_data.get('timestamp'), str):
        timestamp = datetime.fromisoformat(login_data['timestamp'])
    elif isinstance(login_data.get('timestamp'), datetime):
        timestamp = login_data['timestamp']
    else:
        timestamp = datetime.now()
    
    # Feature 1: Hour of day (0-23)
    hour_of_day = timestamp.hour
    
    # Feature 2: Day of week (0-6, Monday=0)
    day_of_week = timestamp.weekday()
    
    # Feature 3: Device similarity score (0-1)
    device_fingerprint = login_data.get('device_fingerprint', '')
    if user_history:
        # Compare with most recent device
        recent_device = user_history[0].get('device_fingerprint', '')
        device_similarity = calculate_device_similarity(device_fingerprint, recent_device)
    else:
        device_similarity = 0.0
    
    # Feature 4: Is known device (0 or 1)
    username = login_data.get('username', '')
    known_device = 1.0 if is_known_device(username, device_fingerprint) else 0.0
    
    # Feature 5: Hours since last login
    hours_since_last = get_hours_since_last_login(username, timestamp)
    
    # Feature 6: Is known location (0 or 1)
    current_location = login_data.get('location', '')
    if user_history and current_location:
        # Check if location appears in recent history (last 10 logins)
        recent_locations = [h.get('location', '') for h in user_history[:10]]
        is_known_loc = 1.0 if current_location in recent_locations else 0.0
    else:
        is_known_loc = 0.0
    
    # Return feature array
    features = np.array([
        hour_of_day,
        day_of_week,
        device_similarity,
        known_device,
        hours_since_last,
        is_known_loc
    ])
    
    return features

# ============================================================================
# MODEL TRAINING
# ============================================================================

def train_user_model(username: str, min_samples: int = 50) -> Dict[str, Any]:
    """
    Train a One-Class SVM model for a specific user
    
    Args:
        username: Username to train model for
        min_samples: Minimum number of samples required for training
    
    Returns:
        Dictionary with training results:
        - success: bool
        - message: str
        - samples_used: int
        - model_path: str (if successful)
    """
    try:
        ensure_models_dir()
        
        # Get user's login history
        print(f"Training model for user: {username}")
        history = get_user_history(username, limit=1000)
        
        if len(history) < min_samples:
            return {
                'success': False,
                'message': f'Insufficient data: {len(history)} samples (minimum {min_samples} required)',
                'samples_used': len(history)
            }
        
        print(f"  Found {len(history)} login attempts")
        
        # Extract features for each historical login
        features_list = []
        
        for i, login in enumerate(history):
            # For each login, use history before it
            prior_history = history[i+1:i+50] if i+1 < len(history) else []
            
            login_data = {
                'timestamp': login['timestamp'],
                'device_fingerprint': login['device_fingerprint'],
                'location': login.get('location'),
                'username': username
            }
            
            features = extract_features(login_data, prior_history)
            features_list.append(features)
        
        # Convert to numpy array
        X = np.array(features_list)
        
        print(f"  Extracted features shape: {X.shape}")
        
        # Train One-Class SVM
        # nu: fraction of outliers expected (0.1 = 10%)
        # gamma: kernel coefficient
        model = OneClassSVM(nu=0.1, gamma='auto', kernel='rbf')
        model.fit(X)
        
        print(f"  Model trained successfully")
        
        # Save model
        model_path = MODELS_DIR / f"{username}_model.pkl"
        joblib.dump(model, model_path)
        
        # Add to loaded models
        _loaded_models[f"{username}_model"] = model
        
        print(f"  Model saved to: {model_path}")
        
        return {
            'success': True,
            'message': f'Model trained successfully with {len(history)} samples',
            'samples_used': len(history),
            'model_path': str(model_path)
        }
        
    except Exception as e:
        error_msg = f"Error training model for {username}: {str(e)}"
        print(f"  {error_msg}")
        return {
            'success': False,
            'message': error_msg,
            'samples_used': 0
        }

# ============================================================================
# RISK SCORING
# ============================================================================

def calculate_risk_score(decision_score: float) -> int:
    """
    Map SVM decision function output to 0-100 risk score
    
    One-Class SVM decision_function returns:
    - Positive values: samples are similar to training data (normal)
    - Negative values: samples are outliers (anomalous)
    
    Risk mapping:
    - Positive score (normal) → low risk (0-30)
    - Near zero → medium risk (30-70)
    - Negative score (anomaly) → high risk (70-100)
    
    Args:
        decision_score: Output from SVM decision_function
    
    Returns:
        Integer risk score from 0 to 100
    """
    # Typical decision_function values range from roughly -2 to +2
    # We'll map this to 0-100 risk score
    
    if decision_score > 0:
        # Normal behavior - low risk
        # Map [0, +inf] to [0, 30]
        # Use exponential decay
        risk = 30 * np.exp(-decision_score)
    else:
        # Anomalous behavior - high risk
        # Map [-inf, 0] to [70, 100]
        # The more negative, the higher the risk
        risk = 70 + 30 * (1 - np.exp(decision_score))
    
    # Ensure risk is in [0, 100]
    risk = max(0, min(100, int(risk)))
    
    return risk

# ============================================================================
# RISK PREDICTION
# ============================================================================

def predict_risk(username: str, login_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict risk score for a login attempt
    
    Args:
        username: Username attempting to login
        login_data: Dictionary containing login information:
            - timestamp: datetime or ISO string
            - device_fingerprint: str
            - location: str (optional)
    
    Returns:
        Dictionary with:
        - risk_score: int (0-100)
        - decision_score: float (raw SVM output)
        - is_anomaly: bool
        - message: str
        - features: dict (extracted features for debugging)
    """
    try:
        # Check if model exists
        model_name = f"{username}_model"
        model = get_model(model_name)
        
        if model is None:
            # Try to load from disk
            model_path = MODELS_DIR / f"{model_name}.pkl"
            if model_path.exists():
                model = joblib.load(model_path)
                _loaded_models[model_name] = model
            else:
                # No model available - return high risk with explanation
                return {
                    'risk_score': 50,  # Medium risk when no model
                    'decision_score': 0.0,
                    'is_anomaly': False,
                    'message': f'No trained model found for user {username}',
                    'features': {}
                }
        
        # Get user history
        user_history = get_user_history(username, limit=50)
        
        # Add username to login data
        login_data['username'] = username
        
        # Extract features
        features = extract_features(login_data, user_history)
        
        # Reshape for prediction (model expects 2D array)
        X = features.reshape(1, -1)
        
        # Get decision function score
        decision_score = model.decision_function(X)[0]
        
        # Calculate risk score (0-100)
        risk_score = calculate_risk_score(decision_score)
        
        # Determine if anomaly (negative decision score)
        is_anomaly = decision_score < 0
        
        # Determine risk level
        if risk_score < 30:
            risk_level = "low"
        elif risk_score < 70:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            'risk_score': risk_score,
            'decision_score': float(decision_score),
            'is_anomaly': is_anomaly,
            'risk_level': risk_level,
            'message': f'Risk assessment complete: {risk_level} risk',
            'features': {
                'hour_of_day': float(features[0]),
                'day_of_week': float(features[1]),
                'device_similarity': float(features[2]),
                'is_known_device': float(features[3]),
                'hours_since_last_login': float(features[4]),
                'is_known_location': float(features[5])
            }
        }
        
    except Exception as e:
        error_msg = f"Error predicting risk: {str(e)}"
        print(error_msg)
        
        return {
            'risk_score': 75,  # High risk on error
            'decision_score': -1.0,
            'is_anomaly': True,
            'risk_level': 'high',
            'message': error_msg,
            'features': {}
        }

# ============================================================================
# BATCH OPERATIONS
# ============================================================================

def train_all_user_models(min_samples: int = 50) -> Dict[str, Any]:
    """
    Train models for all users with sufficient data
    
    Args:
        min_samples: Minimum samples required per user
    
    Returns:
        Dictionary with training results for all users
    """
    from database import list_all_users
    
    users = list_all_users()
    results = {}
    
    print(f"\nTraining models for {len(users)} users...")
    print("=" * 60)
    
    for user in users:
        username = user['username']
        result = train_user_model(username, min_samples=min_samples)
        results[username] = result
        
        if result['success']:
            print(f"✓ {username}: {result['message']}")
        else:
            print(f"✗ {username}: {result['message']}")
    
    print("=" * 60)
    
    successful = sum(1 for r in results.values() if r['success'])
    print(f"\nTraining complete: {successful}/{len(users)} models trained successfully")
    
    return results

def get_model_info(username: str) -> Dict[str, Any]:
    """
    Get information about a user's model
    
    Args:
        username: Username to check
    
    Returns:
        Dictionary with model information
    """
    model_name = f"{username}_model"
    model_path = MODELS_DIR / f"{model_name}.pkl"
    
    info = {
        'username': username,
        'model_exists': model_path.exists(),
        'model_loaded': model_name in _loaded_models,
        'model_path': str(model_path) if model_path.exists() else None
    }
    
    if model_path.exists():
        import os
        stat = os.stat(model_path)
        info['file_size'] = stat.st_size
        info['last_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
    
    return info
    """Save a model to the models directory"""
    ensure_models_dir()
    model_path = MODELS_DIR / f"{model_name}.pkl"
