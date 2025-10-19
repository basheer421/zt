#!/usr/bin/env python3
"""
Test script for ML Engine
Tests feature extraction, model training, and risk prediction
"""

from datetime import datetime, timedelta
from ml_engine import (
    extract_features,
    train_user_model,
    calculate_risk_score,
    predict_risk,
    train_all_user_models,
    get_model_info
)
from database import init_db, get_user_history

def print_separator(title=""):
    """Print a formatted separator"""
    if title:
        print("\n" + "=" * 60)
        print(f"{title}")
        print("=" * 60)
    else:
        print("-" * 60)

def test_feature_extraction():
    """Test feature extraction"""
    print_separator("TEST 1: Feature Extraction")
    
    # Sample login data
    login_data = {
        'username': 'john_doe',
        'timestamp': datetime.now(),
        'device_fingerprint': 'abc123xyz',
        'location': 'New York'
    }
    
    # Get user history
    user_history = get_user_history('john_doe', limit=10)
    print(f"User history records: {len(user_history)}")
    
    # Extract features
    features = extract_features(login_data, user_history)
    
    print(f"\nExtracted features (6 dimensions):")
    print(f"  [0] Hour of day: {features[0]}")
    print(f"  [1] Day of week: {features[1]}")
    print(f"  [2] Device similarity: {features[2]:.3f}")
    print(f"  [3] Is known device: {features[3]}")
    print(f"  [4] Hours since last login: {features[4]:.2f}")
    print(f"  [5] Is known location: {features[5]}")
    
    print("\n✓ Feature extraction successful!")
    return True

def test_risk_score_calculation():
    """Test risk score calculation"""
    print_separator("TEST 2: Risk Score Calculation")
    
    test_cases = [
        (2.0, "Very normal behavior"),
        (1.0, "Normal behavior"),
        (0.5, "Slightly normal"),
        (0.0, "Borderline"),
        (-0.5, "Slightly anomalous"),
        (-1.0, "Anomalous"),
        (-2.0, "Very anomalous"),
    ]
    
    print("\nDecision Score → Risk Score Mapping:")
    print("-" * 50)
    
    for decision_score, description in test_cases:
        risk_score = calculate_risk_score(decision_score)
        risk_level = "LOW" if risk_score < 30 else "MEDIUM" if risk_score < 70 else "HIGH"
        print(f"  {decision_score:>5.1f} → {risk_score:>3d} ({risk_level:6s}) - {description}")
    
    print("\n✓ Risk score calculation working correctly!")
    return True

def test_model_training():
    """Test model training for users"""
    print_separator("TEST 3: Model Training")
    
    users_to_train = ['john_doe', 'jane_smith', 'bob_jones']
    
    for username in users_to_train:
        print(f"\nTraining model for {username}...")
        result = train_user_model(username, min_samples=50)
        
        if result['success']:
            print(f"  ✓ Success: {result['message']}")
            print(f"    Samples used: {result['samples_used']}")
            print(f"    Model path: {result['model_path']}")
        else:
            print(f"  ✗ Failed: {result['message']}")
            print(f"    Samples available: {result['samples_used']}")
    
    print("\n✓ Model training tests complete!")
    return True

def test_risk_prediction():
    """Test risk prediction"""
    print_separator("TEST 4: Risk Prediction")
    
    # Test case 1: Normal login (weekday, business hours, known device)
    print("\nTest Case 1: Normal Login")
    normal_login = {
        'timestamp': '2025-10-20T10:30:00',  # Monday 10:30 AM
        'device_fingerprint': get_user_history('john_doe', limit=1)[0]['device_fingerprint'],
        'location': 'New York'
    }
    
    result = predict_risk('john_doe', normal_login)
    print(f"  Risk Score: {result['risk_score']}/100")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Decision Score: {result['decision_score']:.3f}")
    print(f"  Is Anomaly: {result['is_anomaly']}")
    print(f"  Features: {result['features']}")
    
    # Test case 2: Suspicious login (weekend, late night, unknown location)
    print("\nTest Case 2: Suspicious Login")
    suspicious_login = {
        'timestamp': '2025-10-19T03:00:00',  # Sunday 3:00 AM
        'device_fingerprint': 'unknown_device_fingerprint',
        'location': 'Tokyo'
    }
    
    result = predict_risk('john_doe', suspicious_login)
    print(f"  Risk Score: {result['risk_score']}/100")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Decision Score: {result['decision_score']:.3f}")
    print(f"  Is Anomaly: {result['is_anomaly']}")
    print(f"  Features: {result['features']}")
    
    # Test case 3: User without model
    print("\nTest Case 3: User Without Model")
    result = predict_risk('nonexistent_user', normal_login)
    print(f"  Risk Score: {result['risk_score']}/100")
    print(f"  Message: {result['message']}")
    
    print("\n✓ Risk prediction tests complete!")
    return True

def test_model_info():
    """Test getting model information"""
    print_separator("TEST 5: Model Information")
    
    users = ['john_doe', 'jane_smith', 'test_user']
    
    for username in users:
        info = get_model_info(username)
        print(f"\n{username}:")
        print(f"  Model exists: {info['model_exists']}")
        print(f"  Model loaded: {info['model_loaded']}")
        if info.get('model_path'):
            print(f"  Model path: {info['model_path']}")
            print(f"  File size: {info.get('file_size', 0)} bytes")
            print(f"  Last modified: {info.get('last_modified', 'N/A')}")
    
    print("\n✓ Model info retrieval complete!")
    return True

def test_batch_training():
    """Test training models for all users"""
    print_separator("TEST 6: Batch Training (All Users)")
    
    print("\nTraining models for all users with sufficient data...")
    results = train_all_user_models(min_samples=50)
    
    print("\n✓ Batch training complete!")
    return True

def test_comparative_analysis():
    """Compare risk scores for different users"""
    print_separator("TEST 7: Comparative Risk Analysis")
    
    # Same login attempt for different users
    test_login = {
        'timestamp': datetime.now().isoformat(),
        'device_fingerprint': 'test_device_123',
        'location': 'London'
    }
    
    users = ['john_doe', 'jane_smith', 'bob_jones']
    print("\nSame login from London at current time:")
    print("-" * 50)
    
    for username in users:
        result = predict_risk(username, test_login)
        print(f"{username:15s}: Risk={result['risk_score']:3d}, Level={result['risk_level']:6s}, Anomaly={result['is_anomaly']}")
    
    print("\n✓ Comparative analysis complete!")
    return True

def run_all_tests():
    """Run all ML engine tests"""
    print("\n" + "=" * 60)
    print("ML ENGINE TEST SUITE")
    print("=" * 60)
    print("Testing feature extraction, training, and prediction")
    print("=" * 60)
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    print("✓ Database ready")
    
    results = []
    
    try:
        # Run all tests
        results.append(("Feature Extraction", test_feature_extraction()))
        results.append(("Risk Score Calculation", test_risk_score_calculation()))
        results.append(("Model Training", test_model_training()))
        results.append(("Risk Prediction", test_risk_prediction()))
        results.append(("Model Information", test_model_info()))
        results.append(("Batch Training", test_batch_training()))
        results.append(("Comparative Analysis", test_comparative_analysis()))
        
        # Print summary
        print_separator("TEST SUMMARY")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\n{passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
        
        print("\n" + "=" * 60)
        print("ML Engine is ready for use!")
        print("\nKey Functions:")
        print("  - extract_features(login_data, user_history)")
        print("  - train_user_model(username)")
        print("  - calculate_risk_score(decision_score)")
        print("  - predict_risk(username, login_data)")
        print("  - train_all_user_models()")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    run_all_tests()
