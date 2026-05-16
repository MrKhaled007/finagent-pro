# agents/analyst_agent.py
import pickle
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap
import io
import base64
from agents.base_agent import BaseAgent
from tools.feature_engineering import compute_features, FEATURE_COLS

class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("analyst")
        with open("models/risk_model.pkl", "rb") as f:
            bundle = pickle.load(f)
        self.risk_model = bundle["model"]
        self.feature_cols = bundle["feature_cols"]
        self.explainer = shap.TreeExplainer(self.risk_model)

    def run(self, ticker: str, research_brief: str = "") -> dict:
        print(f"[analyst] Computing features for {ticker}...")
        features = compute_features(ticker)

        if "error" in features:
            return {"error": features["error"]}

        # Build feature vector
        import pandas as pd
        X = pd.DataFrame([{col: features[col] for col in self.feature_cols}])

        # Risk prediction
        prob = self.risk_model.predict_proba(X)[0][1]  # probability of high risk
        risk_score = round(float(prob) * 100, 1)
        risk_label = "HIGH" if float(prob) >= 0.5 else "LOW"

        # SHAP values
        shap_values = self.explainer.shap_values(X)

        # Handle both old and new SHAP output formats
        if isinstance(shap_values, list):
            sv = shap_values[1][0]  # class 1 (high risk)
        else:
            sv = shap_values[0] if shap_values.ndim == 1 else shap_values[0]

        # Top 5 risk factors
        shap_dict = dict(zip(self.feature_cols, sv))
        sorted_factors = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

        # Generate SHAP bar chart
        shap_chart_b64 = self._generate_shap_chart(sorted_factors, ticker, risk_score)

        # Gemini explanation
        explanation = self._explain(ticker, risk_score, risk_label, features, sorted_factors, research_brief)

        return {
            "ticker": ticker,
            "risk_score": risk_score,
            "risk_label": risk_label,
            "risk_probability": round(float(prob), 4),
            "top_factors": [
                {"factor": k, "shap_value": round(float(v), 4)}
                for k, v in sorted_factors
            ],
            "features": features,
            "shap_chart_b64": shap_chart_b64,
            "explanation": explanation,
        }

    def _generate_shap_chart(self, sorted_factors, ticker, risk_score):
        factors = [f[0] for f in sorted_factors]
        values = [f[1] for f in sorted_factors]
        colors = ["#D85A30" if v > 0 else "#1D9E75" for v in values]

        fig, ax = plt.subplots(figsize=(6, 3.5))
        bars = ax.barh(factors[::-1], values[::-1], color=colors[::-1])
        ax.axvline(0, color="gray", linewidth=0.8, linestyle="--")
        ax.set_title(f"{ticker} — Risk Factors (SHAP)", fontsize=12, fontweight="bold")
        ax.set_xlabel("SHAP value (impact on risk score)")
        ax.tick_params(axis="y", labelsize=9)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    def _explain(self, ticker, risk_score, risk_label, features, sorted_factors, research_brief):
        factors_text = "\n".join(
            [f"  - {k}: SHAP={v:.4f}" for k, v in sorted_factors]
        )
        prompt = f"""
You are a quantitative risk analyst. Explain the risk assessment for {ticker} in plain English.

Risk Score: {risk_score}/100 ({risk_label} RISK)

Key metrics:
- RSI: {features['rsi_14']} (>70 = overbought, <30 = oversold)
- Volatility (20d annualised): {features['volatility_20d']}%
- 1-Month Momentum: {features['mom_1m']}%
- PE Ratio: {features['pe_ratio']}
- Debt/Equity: {features['debt_to_equity']}
- Profit Margin: {features['profit_margin']}
- 52-Week Position: {features['position_52w']}% (100=at high, 0=at low)

Top 5 risk drivers (SHAP values — positive = increases risk):
{factors_text}

Research context:
{research_brief[:500] if research_brief else 'Not provided.'}

Write 3-4 sentences explaining:
1. What the risk score means for this stock
2. Which 2-3 factors are driving the risk most
3. One actionable insight for an investor

Be specific, cite the actual numbers, and keep it under 100 words.
"""
        return self.call_gemini(prompt)