import pickle
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Model storage
MODELS_DIR = Path(__file__).parent / "models"
_loaded_models: Dict[str, Any] = {}

def ensure_models_dir():
    """Ensure models directory exists"""
    MODELS_DIR.mkdir(exist_ok=True)
    print(f"Models directory: {MODELS_DIR}")

def load_models():
    """Load all .pkl models from the models directory"""
    ensure_models_dir()
    global _loaded_models
    
    print("Loading ML models...")
    model_files = list(MODELS_DIR.glob("*.pkl"))
    
    if not model_files:
        print("No .pkl model files found in models directory")
        return
    
    for model_path in model_files:
        try:
            model_name = model_path.stem
            with open(model_path, 'rb') as f:
                _loaded_models[model_name] = pickle.load(f)
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

def save_model(model: Any, model_name: str):
    """Save a model to the models directory"""
    ensure_models_dir()
    model_path = MODELS_DIR / f"{model_name}.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Add to loaded models
    _loaded_models[model_name] = model
    print(f"Model saved: {model_name}")

def predict(model_name: str, input_data: Any) -> Dict[str, Any]:
    """
    Make a prediction using a loaded model
    
    Args:
        model_name: Name of the model to use
        input_data: Input data for prediction (dict, list, or numpy array)
    
    Returns:
        Dictionary with prediction results
    """
    model = get_model(model_name)
    
    if model is None:
        raise ValueError(f"Model '{model_name}' not found. Available models: {list_available_models()}")
    
    try:
        # Convert input to appropriate format
        if isinstance(input_data, dict):
            # Convert dict to DataFrame for sklearn models
            df = pd.DataFrame([input_data])
            X = df.values
        elif isinstance(input_data, list):
            X = np.array(input_data).reshape(1, -1)
        else:
            X = input_data
        
        # Make prediction
        prediction = model.predict(X)
        
        # Try to get prediction probability if available
        confidence = None
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X)
            confidence = float(np.max(proba))
        
        return {
            "model_name": model_name,
            "prediction": prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
            "confidence": confidence,
            "success": True
        }
    
    except Exception as e:
        return {
            "model_name": model_name,
            "error": str(e),
            "success": False
        }

def batch_predict(model_name: str, input_data_list: List[Any]) -> List[Dict[str, Any]]:
    """Make predictions for multiple inputs"""
    return [predict(model_name, data) for data in input_data_list]

# Example: Create a simple dummy model for testing
def create_dummy_model():
    """Create a simple dummy model for testing purposes"""
    from sklearn.linear_model import LogisticRegression
    from sklearn.datasets import make_classification
    
    # Generate dummy data
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)
    
    # Train a simple model
    model = LogisticRegression(random_state=42)
    model.fit(X, y)
    
    # Save the model
    save_model(model, "dummy_classifier")
    print("Dummy classifier model created and saved")
    
    return model

# Preprocessing utilities
def preprocess_data(data: pd.DataFrame, scaler: Optional[StandardScaler] = None) -> np.ndarray:
    """Preprocess data for model input"""
    if scaler is None:
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data)
    else:
        scaled_data = scaler.transform(data)
    
    return scaled_data

def extract_features(raw_data: Dict[str, Any]) -> np.ndarray:
    """Extract features from raw input data"""
    # Implement your feature extraction logic here
    # This is a placeholder example
    features = []
    for key, value in raw_data.items():
        if isinstance(value, (int, float)):
            features.append(value)
    
    return np.array(features).reshape(1, -1)
