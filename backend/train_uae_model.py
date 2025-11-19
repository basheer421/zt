#!/usr/bin/env python3
"""
Train UAE-focused SVM model on Kaggle RBA dataset
Treats UAE and Gulf countries as normal baseline
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib
from pathlib import Path
import ipaddress
from datetime import datetime

# Paths
DATASET_PATH = Path(__file__).parent / "dataset" / "rba-dataset.csv"
MODELS_DIR = Path(__file__).parent / "models"
GLOBAL_MODEL_PATH = MODELS_DIR / "global_model.pkl"

# UAE deployment settings
SAMPLE_SIZE = 250000
UAE_GULF_COUNTRIES = ['AE', 'SA', 'QA', 'KW', 'OM', 'BH']  # UAE and Gulf states
REGIONAL_COUNTRIES = ['JO', 'LB', 'EG', 'IN', 'PK']  # Regional partners

print("=" * 80)
print("TRAINING UAE-FOCUSED ANOMALY DETECTION MODEL")
print("=" * 80)
print(f"Dataset: {DATASET_PATH}")
print(f"Target deployment: United Arab Emirates (UAE)")
print(f"Sample size: {SAMPLE_SIZE:,} rows")
print("=" * 80)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n[1/6] Loading data with UAE focus...")
print("   Prioritizing UAE and Gulf region traffic...")

# Load data and give preference to UAE traffic
anomalies = []
uae_samples = []
regional_samples = []
other_samples = []
chunk_size = 100000
rows_to_read = min(SAMPLE_SIZE * 20, 10000000)

for chunk in pd.read_csv(DATASET_PATH, chunksize=chunk_size, nrows=rows_to_read):
    # Separate anomalies
    chunk_anomalies = chunk[chunk['Is Account Takeover'] == True]
    chunk_normal = chunk[chunk['Is Account Takeover'] == False]
    
    if len(chunk_anomalies) > 0:
        anomalies.append(chunk_anomalies)
    
    # Prioritize UAE and Gulf countries
    uae_gulf = chunk_normal[chunk_normal['Country'].isin(UAE_GULF_COUNTRIES)]
    if len(uae_gulf) > 0:
        uae_samples.append(uae_gulf)
    
    # Include regional countries with lower priority
    regional = chunk_normal[chunk_normal['Country'].isin(REGIONAL_COUNTRIES)]
    if len(regional) > 0:
        regional_samples.append(regional.sample(n=min(len(regional), 1000), random_state=42))
    
    # Sample from other countries
    other = chunk_normal[~chunk_normal['Country'].isin(UAE_GULF_COUNTRIES + REGIONAL_COUNTRIES)]
    if len(other) > 0:
        sample_size = min(len(other), chunk_size // 20)
        other_samples.append(other.sample(n=sample_size, random_state=42))

# Combine all data
data_anomalies = pd.concat(anomalies, ignore_index=True) if anomalies else pd.DataFrame()
data_uae = pd.concat(uae_samples, ignore_index=True) if uae_samples else pd.DataFrame()
data_regional = pd.concat(regional_samples, ignore_index=True) if regional_samples else pd.DataFrame()
data_other = pd.concat(other_samples, ignore_index=True) if other_samples else pd.DataFrame()

print(f"   UAE/Gulf samples: {len(data_uae):,}")
print(f"   Regional samples: {len(data_regional):,}")
print(f"   Other samples: {len(data_other):,}")
print(f"   Anomalies: {len(data_anomalies):,}")

# Combine and balance the dataset
# Priority: All UAE/Gulf, some regional, some others
target_uae = min(len(data_uae), SAMPLE_SIZE // 2)  # 50% UAE if available
target_regional = SAMPLE_SIZE // 4  # 25% regional
target_other = SAMPLE_SIZE // 4  # 25% other

final_uae = data_uae.sample(n=min(len(data_uae), target_uae), random_state=42) if len(data_uae) > 0 else pd.DataFrame()
final_regional = data_regional.sample(n=min(len(data_regional), target_regional), random_state=42) if len(data_regional) > 0 else pd.DataFrame()
final_other = data_other.sample(n=min(len(data_other), target_other), random_state=42) if len(data_other) > 0 else pd.DataFrame()

data = pd.concat([final_uae, final_regional, final_other, data_anomalies], ignore_index=True)

print(f"   Final dataset: {len(data):,} rows")
print(f"   Anomalies: {len(data_anomalies):,}")
print(f"   Normal: {len(data) - len(data_anomalies):,}")

# ============================================================================
# PREPROCESS DATA
# ============================================================================

print("\n[2/6] Preprocessing data...")

# Convert categorical strings to numeric codes
print("   Encoding categorical string columns...")
data['User Agent String'] = data['User Agent String'].astype('category').cat.codes
data['Browser Name and Version'] = data['Browser Name and Version'].astype('category').cat.codes
data['OS Name and Version'] = data['OS Name and Version'].astype('category').cat.codes

# Convert IP addresses to integers
print("   Converting IP addresses to integers...")
def ip_to_int(ip_str):
    try:
        return int(ipaddress.IPv4Address(str(ip_str)))
    except:
        return 0

data['IP Address'] = data['IP Address'].apply(ip_to_int)

# Extract hour from timestamp
data['Login Hour'] = pd.to_datetime(data['Login Timestamp']).dt.hour

# Select features matching Kaggle approach
numeric_cols = [
    'ASN',
    'Login Hour',
    'IP Address',
    'User Agent String',
    'Browser Name and Version',
    'OS Name and Version'
]

categorical_cols = [
    'Country',
    'Device Type'
]

print(f"   Numeric features: {numeric_cols}")
print(f"   Categorical features: {categorical_cols}")

# ============================================================================
# PREPARE TRAINING DATA
# ============================================================================

print("\n[3/6] Preparing training data...")

# Prepare features and labels
features = data[numeric_cols + categorical_cols]
labels = data['Is Account Takeover'].astype(int)

print(f"   Features shape: {features.shape}")
print(f"   Labels distribution:")
print(f"      Normal logins: {(labels == 0).sum():,} ({(labels == 0).sum() / len(labels) * 100:.2f}%)")
print(f"      Account takeovers: {(labels == 1).sum():,} ({(labels == 1).sum() / len(labels) * 100:.2f}%)")

# ============================================================================
# SPLIT DATA
# ============================================================================

print("\n[4/6] Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"   Training set: {len(X_train):,} samples")
print(f"   Test set: {len(X_test):,} samples")

# ============================================================================
# CREATE AND TRAIN MODEL
# ============================================================================

print("\n[5/6] Training UAE-focused SVM model...")
print("   This may take several minutes...")

# Create preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ])

# Create full pipeline with SVM
# Using higher C value and scale_pos_weight approach for better sensitivity
from sklearn.calibration import CalibratedClassifierCV

# First train base SVM
base_svm = SVC(
    kernel='rbf', 
    C=10.0,  # Higher C for less regularization, more sensitivity
    gamma='scale',  # Better default than 'auto'
    class_weight='balanced',
    random_state=42
)

# Wrap in calibration for better probability estimates
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', CalibratedClassifierCV(
        base_svm,
        method='sigmoid',  # Platt scaling
        cv=3  # 3-fold cross-validation
    ))
])

# Train the model
start_time = datetime.now()
print(f"   Training started at: {start_time.strftime('%H:%M:%S')}")

pipeline.fit(X_train, y_train)

end_time = datetime.now()
training_duration = (end_time - start_time).total_seconds()
print(f"   Training completed at: {end_time.strftime('%H:%M:%S')}")
print(f"   Duration: {training_duration:.1f} seconds ({training_duration / 60:.1f} minutes)")

# ============================================================================
# EVALUATE MODEL
# ============================================================================

print("\n[6/6] Evaluating model...")

# Predictions
y_pred = pipeline.predict(X_test)
y_pred_proba = pipeline.predict_proba(X_test)[:, 1]

# Confusion matrix
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

# Calculate AUC
try:
    auc = roc_auc_score(y_test, y_pred_proba)
except:
    auc = 0.5

# Accuracy
accuracy = (tp + tn) / (tp + tn + fp + fn)

print("\n" + "=" * 80)
print("MODEL PERFORMANCE")
print("=" * 80)
print(f"\nConfusion Matrix:")
print(f"   True Negatives:  {tn:,}")
print(f"   False Positives: {fp:,}")
print(f"   False Negatives: {fn:,}")
print(f"   True Positives:  {tp:,}")

print(f"\nAccuracy: {accuracy * 100:.2f}%")
print(f"AUC Score: {auc:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, 
                          target_names=['Normal', 'Account Takeover']))

# ============================================================================
# SAVE MODEL
# ============================================================================

print("\n" + "=" * 80)
print("SAVING MODEL")
print("=" * 80)

MODELS_DIR.mkdir(exist_ok=True)
joblib.dump(pipeline, GLOBAL_MODEL_PATH)

model_size_mb = GLOBAL_MODEL_PATH.stat().st_size / (1024 * 1024)

print(f"✓ Model saved to: {GLOBAL_MODEL_PATH}")
print(f"✓ Model size: {model_size_mb:.2f} MB")
print(f"✓ Trained on: {len(data):,} samples ({len(data_uae):,} UAE/Gulf)")
print(f"✓ Training time: {training_duration:.1f} seconds")
print(f"✓ AUC Score: {auc:.4f}")

print("\n" + "=" * 80)
print("TRAINING COMPLETE!")
print("=" * 80)
print("\nThe UAE-focused model is ready for deployment.")
print("It will treat UAE and Gulf countries as normal baseline.")
print("=" * 80)
