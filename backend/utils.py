import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

# Paths inside the backend/model directory.
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "model")
DATASET_CSV = os.path.join(MODEL_DIR, "dataset.csv")
MODEL_PKL = os.path.join(MODEL_DIR, "model.pkl")

TRANSACTION_TYPES = ["online", "pos", "atm"]
FEATURE_COLUMNS = ["amount", "hour", "location_change", "device_change", "online", "pos", "atm"]


def generate_dummy_dataset(n_samples=1000, save_path=DATASET_CSV):
    """Generate a dummy fraud dataset programmatically and save it to CSV."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    rng = np.random.default_rng(42)
    rows = []

    for _ in range(n_samples):
        amount = round(float(rng.uniform(5.0, 5000.0)), 2)
        hour = int(rng.integers(0, 24))
        location_change = int(rng.random() < 0.18)
        device_change = int(rng.random() < 0.15)
        transaction_type = str(rng.choice(TRANSACTION_TYPES, p=[0.55, 0.30, 0.15]))

        # Build a simple behavior-driven risk score for synthetic labeling.
        rule_score = 0.0
        if amount > 3000:
            rule_score += 1.3
        if hour < 6 or hour > 22:
            rule_score += 0.9
        if location_change:
            rule_score += 0.9
        if device_change:
            rule_score += 0.9
        if transaction_type == "online":
            rule_score += 0.5

        # Convert the behavior score into a fraud label with noise.
        fraud_probability = 1 / (1 + np.exp(-(rule_score - 1.8)))
        fraud_probability = min(max(fraud_probability + rng.normal(0, 0.12), 0.0), 1.0)
        is_fraud = int(fraud_probability > 0.55)

        rows.append({
            "amount": amount,
            "hour": hour,
            "location_change": location_change,
            "device_change": device_change,
            "transaction_type": transaction_type,
            "is_fraud": is_fraud,
        })

    df = pd.DataFrame(rows)
    df.to_csv(save_path, index=False)
    return df


def _encode_transaction_type(df):
    """Encode transaction_type into one-hot columns for the model."""
    encoded = pd.DataFrame(
        {
            "online": (df["transaction_type"] == "online").astype(int),
            "pos": (df["transaction_type"] == "pos").astype(int),
            "atm": (df["transaction_type"] == "atm").astype(int),
        }
    )
    return pd.concat([df[["amount", "hour", "location_change", "device_change"]], encoded], axis=1)


def train_rf_model(dataset_path=DATASET_CSV, model_path=MODEL_PKL):
    """Train a RandomForestClassifier on the dummy dataset and save the model."""
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    df = pd.read_csv(dataset_path)
    X = _encode_transaction_type(df)
    y = df["is_fraud"]

    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    model.fit(X, y)
    joblib.dump(model, model_path)
    return model


def load_model(model_path=MODEL_PKL):
    """Load a trained model, training it first if missing."""
    if not os.path.exists(model_path):
        if not os.path.exists(DATASET_CSV):
            generate_dummy_dataset()
        train_rf_model()
    return joblib.load(model_path)


def rule_based_risk(transaction):
    """Compute a rule-based risk score and explainable reasons from transaction behavior."""
    reasons = []
    score = 0.0

    if transaction.amount > 3000:
        reasons.append("High amount")
        score += 1.0

    if transaction.hour < 6 or transaction.hour > 22:
        reasons.append("Odd time")
        score += 0.7

    if transaction.device_change == 1:
        reasons.append("New device")
        score += 0.6

    if transaction.location_change == 1:
        reasons.append("New location")
        score += 0.6

    # Normalize to a 0-1 risk score.
    rule_score = min(score / 2.8, 1.0)
    return rule_score, reasons


def combine_risk(ml_risk, rule_risk):
    """Combine ML model probability with rule-based risk to produce a final score."""
    return float((ml_risk + rule_risk) / 2.0)


def prepare_features(transaction):
    """Create the same feature vector used during model training."""
    return [
        transaction.amount,
        transaction.hour,
        transaction.location_change,
        transaction.device_change,
        1 if transaction.transaction_type == "online" else 0,
        1 if transaction.transaction_type == "pos" else 0,
        1 if transaction.transaction_type == "atm" else 0,
    ]
