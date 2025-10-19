#!/usr/bin/env python3
"""
Train ML models for all users in the database
Run this script after seeding the database to create initial models
"""

import os
from pathlib import Path
from database import init_db, list_all_users, get_user_history
from ml_engine import train_user_model, train_all_user_models, get_model_info, MODELS_DIR

def print_separator(title="", char="="):
    """Print a formatted separator"""
    if title:
        print("\n" + char * 60)
        print(f"{title}")
        print(char * 60)
    else:
        print(char * 60)

def check_user_data():
    """Check which users have sufficient data for training"""
    print_separator("CHECKING USER DATA")
    
    users = list_all_users()
    print(f"\nFound {len(users)} users in database:")
    print("-" * 60)
    
    users_with_data = []
    
    for user in users:
        username = user['username']
        history = get_user_history(username, limit=1000)
        
        status_icon = "✓" if len(history) >= 50 else "✗"
        status = "Ready" if len(history) >= 50 else "Insufficient data"
        
        print(f"{status_icon} {username:20s} - {len(history):4d} login attempts - {status}")
        
        if len(history) >= 50:
            users_with_data.append((username, len(history)))
    
    print("-" * 60)
    print(f"\nUsers ready for training: {len(users_with_data)}/{len(users)}")
    
    return users_with_data

def train_models_individually(min_samples: int = 50):
    """Train models for each user individually with detailed output"""
    print_separator("TRAINING MODELS INDIVIDUALLY")
    
    users = list_all_users()
    results = {}
    
    for i, user in enumerate(users, 1):
        username = user['username']
        print(f"\n[{i}/{len(users)}] Training model for: {username}")
        print("-" * 60)
        
        result = train_user_model(username, min_samples=min_samples)
        results[username] = result
        
        if result['success']:
            print(f"✓ SUCCESS")
            print(f"  Message: {result['message']}")
            print(f"  Samples: {result['samples_used']}")
            print(f"  Path: {result['model_path']}")
        else:
            print(f"✗ FAILED")
            print(f"  Reason: {result['message']}")
            print(f"  Samples: {result['samples_used']}")
    
    return results

def list_created_models():
    """List all created model files"""
    print_separator("CREATED MODEL FILES")
    
    model_files = sorted(MODELS_DIR.glob("*_model.pkl"))
    
    if not model_files:
        print("\n⚠ No model files found!")
        return []
    
    print(f"\nFound {len(model_files)} model file(s):")
    print("-" * 60)
    
    total_size = 0
    
    for model_path in model_files:
        username = model_path.stem.replace('_model', '')
        file_size = model_path.stat().st_size
        total_size += file_size
        
        # Get model info
        info = get_model_info(username)
        
        print(f"✓ {model_path.name}")
        print(f"    User: {username}")
        print(f"    Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        print(f"    Path: {model_path}")
        if info.get('last_modified'):
            print(f"    Modified: {info['last_modified']}")
        print()
    
    print("-" * 60)
    print(f"Total: {len(model_files)} models, {total_size:,} bytes ({total_size / 1024:.2f} KB)")
    
    return model_files

def print_training_summary(results: dict):
    """Print a summary of training results"""
    print_separator("TRAINING SUMMARY")
    
    successful = [username for username, result in results.items() if result['success']]
    failed = [username for username, result in results.items() if not result['success']]
    
    print(f"\nTotal users: {len(results)}")
    print(f"Successfully trained: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print(f"\n✓ Successfully trained models:")
        for username in successful:
            samples = results[username]['samples_used']
            print(f"  - {username} ({samples} samples)")
    
    if failed:
        print(f"\n✗ Failed to train models:")
        for username in failed:
            reason = results[username]['message']
            print(f"  - {username}: {reason}")
    
    print("-" * 60)
    
    if failed:
        print(f"\nℹ️  Note: Users need at least 50 login attempts for training.")
        print(f"   Run seed_data.py to generate more training data.")

def verify_models():
    """Verify that models can be loaded and used"""
    print_separator("VERIFYING MODELS")
    
    model_files = list(MODELS_DIR.glob("*_model.pkl"))
    
    if not model_files:
        print("\n⚠ No models to verify!")
        return False
    
    print(f"\nVerifying {len(model_files)} model(s)...")
    print("-" * 60)
    
    from ml_engine import predict_risk
    from datetime import datetime
    
    all_valid = True
    
    for model_path in model_files:
        username = model_path.stem.replace('_model', '')
        
        try:
            # Try to make a prediction with the model
            test_login = {
                'timestamp': datetime.now().isoformat(),
                'device_fingerprint': 'test_verification_device',
                'location': 'Test Location'
            }
            
            result = predict_risk(username, test_login)
            
            if 'risk_score' in result:
                print(f"✓ {username:20s} - Model valid (risk score: {result['risk_score']})")
            else:
                print(f"✗ {username:20s} - Model loaded but prediction failed")
                all_valid = False
        
        except Exception as e:
            print(f"✗ {username:20s} - Error: {str(e)}")
            all_valid = False
    
    print("-" * 60)
    
    if all_valid:
        print("\n✓ All models verified successfully!")
    else:
        print("\n⚠ Some models failed verification")
    
    return all_valid

def main():
    """Main function to train all models"""
    print("\n" + "=" * 60)
    print("ML MODEL TRAINING SCRIPT")
    print("=" * 60)
    print("This script trains OneClassSVM models for user behavior analysis")
    print("=" * 60)
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Check user data
    users_with_data = check_user_data()
    
    if not users_with_data:
        print("\n⚠️  No users have sufficient data for training!")
        print("\nPlease run seed_data.py first to generate training data:")
        print("  python3 seed_data.py")
        print("\nMinimum required: 50 login attempts per user")
        return
    
    # Ask for confirmation
    print(f"\nReady to train models for {len(users_with_data)} user(s)")
    
    # Train models using batch function
    print_separator("STARTING BATCH TRAINING")
    print("\nTraining all user models...")
    results = train_all_user_models(min_samples=50)
    
    # Print summary
    print_training_summary(results)
    
    # List created models
    model_files = list_created_models()
    
    # Verify models
    if model_files:
        verify_models()
    
    # Final message
    print_separator("TRAINING COMPLETE", "=")
    
    if model_files:
        print("\n✓ Model training completed successfully!")
        print(f"\nModels are saved in: {MODELS_DIR}")
        print(f"Total models created: {len(model_files)}")
        print("\nThese models can now be used for risk prediction:")
        print("  from ml_engine import predict_risk")
        print("  result = predict_risk('username', login_data)")
        print("\nNext steps:")
        print("  1. Test risk prediction: python3 test_ml_engine.py")
        print("  2. Start the API server: python3 main.py")
        print("  3. Use /api/authenticate endpoint for login verification")
    else:
        print("\n⚠️  No models were created!")
        print("Please check that you have sufficient training data.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print("=" * 60)
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        exit(1)
