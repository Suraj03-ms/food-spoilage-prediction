import pandas as pd
import pickle
import os
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("Datasets/food.csv", low_memory=False)

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())

# Fill missing values
df = df.fillna("Unknown")

# ─────────────────────────────────────────────
# BETTER FEATURES: using more informative columns
# Previously only 3 columns → 42% accuracy
# Now using 7 columns including violation info
# ─────────────────────────────────────────────
features = [
    "businessname",
    "city",
    "address",
    "licensecat",   # type of food license
    "descript",     # business description
    "viollevel",    # violation level (critical/non-critical)
    "violstatus",   # status of violation
]

# Copy selected feature columns
X = df[features].copy()

# Target column
y = df["result"].copy()

# Encode each feature column with its own LabelEncoder
encoders = {}
for col in X.columns:
    le = LabelEncoder()
    X.loc[:, col] = le.fit_transform(X[col].astype(str))
    encoders[col] = le

# Encode target AND save encoder so app.py can decode back to label
target_encoder = LabelEncoder()
y_encoded = target_encoder.fit_transform(y.astype(str))

print("\nTarget classes:", target_encoder.classes_)
print("Number of classes:", len(target_encoder.classes_))

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

print(f"\nTraining on {len(X_train):,} samples, testing on {len(X_test):,} samples...")

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")

# FIX: only use labels that actually appear in y_test to avoid size mismatch crash
labels_in_test = np.unique(y_test)
class_names_in_test = target_encoder.inverse_transform(labels_in_test)

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    labels=labels_in_test,
    target_names=class_names_in_test
))

# Feature importance
print("\nFeature Importances:")
for feat, imp in sorted(zip(features, model.feature_importances_), key=lambda x: -x[1]):
    print(f"  {feat:20s}: {imp:.4f}")

# Save all artifacts
os.makedirs("models", exist_ok=True)
pickle.dump(model,          open("models/model.pkl",          "wb"))
pickle.dump(encoders,       open("models/encoders.pkl",       "wb"))
pickle.dump(features,       open("models/features.pkl",       "wb"))
pickle.dump(target_encoder, open("models/target_encoder.pkl", "wb"))

print("\n✅ Saved: model.pkl, encoders.pkl, features.pkl, target_encoder.pkl")
print("✅ You can now run: python app.py")