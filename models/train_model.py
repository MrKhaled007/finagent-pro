# models/train_model.py
import pickle
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Feature columns — must match compute_features() output
FEATURE_COLS = [
    "mom_1m", "mom_3m", "mom_1y",
    "volatility_20d", "rsi_14", "position_52w",
    "volume_trend", "pe_ratio", "debt_to_equity", "profit_margin"
]

def generate_synthetic_data(n=2000, seed=42):
    """
    Generate realistic synthetic training data.
    High risk = high volatility + high PE + overbought RSI + high debt.
    """
    np.random.seed(seed)
    data = {
        "mom_1m":        np.random.normal(0, 8, n),
        "mom_3m":        np.random.normal(0, 15, n),
        "mom_1y":        np.random.normal(10, 30, n),
        "volatility_20d": np.abs(np.random.normal(25, 15, n)),
        "rsi_14":        np.random.uniform(20, 80, n),
        "position_52w":  np.random.uniform(0, 100, n),
        "volume_trend":  np.random.normal(0, 20, n),
        "pe_ratio":      np.abs(np.random.normal(22, 15, n)),
        "debt_to_equity": np.abs(np.random.normal(60, 50, n)),
        "profit_margin": np.random.uniform(-0.1, 0.4, n),
    }
    df = pd.DataFrame(data)

    # Risk label logic — mirrors real financial intuition
    risk_score = (
        (df["volatility_20d"] > 35).astype(int) * 2 +
        (df["rsi_14"] > 70).astype(int) * 1 +
        (df["pe_ratio"] > 40).astype(int) * 1 +
        (df["debt_to_equity"] > 100).astype(int) * 1 +
        (df["profit_margin"] < 0).astype(int) * 2 +
        (df["mom_1m"] < -10).astype(int) * 1
    )
    df["risk_label"] = (risk_score >= 3).astype(int)  # 1 = high risk

    return df

def train_and_save():
    print("Generating training data...")
    df = generate_synthetic_data(n=2000)

    X = df[FEATURE_COLS]
    y = df["risk_label"]

    print(f"Class distribution: {y.value_counts().to_dict()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training XGBoost model...")
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss",
        verbosity=0,
    )
    model.fit(X_train, y_train)

    print("\nModel evaluation:")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["Low Risk", "High Risk"]))

    # Save model + feature columns together
    bundle = {"model": model, "feature_cols": FEATURE_COLS}
    with open("models/risk_model.pkl", "wb") as f:
        pickle.dump(bundle, f)

    print("✅ Model saved to models/risk_model.pkl")

if __name__ == "__main__":
    train_and_save()