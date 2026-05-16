# tools/feature_engineering.py
import numpy as np
import pandas as pd
import yfinance as yf

FEATURE_COLS = [
    "mom_1m", "mom_3m", "mom_1y",
    "volatility_20d", "rsi_14", "position_52w",
    "volume_trend", "pe_ratio", "debt_to_equity", "profit_margin"
]

def compute_features(ticker: str) -> dict:
    """Compute ML features from raw price + fundamental data."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        info = stock.info

        if hist.empty or len(hist) < 30:
            return {"error": f"Not enough price history for {ticker}"}

        close = hist["Close"]
        volume = hist["Volume"]

        # --- Price momentum ---
        mom_1m = (close.iloc[-1] - close.iloc[-22]) / close.iloc[-22] * 100
        mom_3m = (close.iloc[-1] - close.iloc[-66]) / close.iloc[-66] * 100 if len(close) > 66 else 0
        mom_1y = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100

        # --- Volatility (20-day rolling std of daily returns) ---
        daily_returns = close.pct_change().dropna()
        volatility_20d = daily_returns.tail(20).std() * np.sqrt(252) * 100  # annualised %

        # --- RSI (14-day) ---
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]

        # --- 52-week position (where is price in its annual range?) ---
        high_52w = close.max()
        low_52w = close.min()
        position_52w = (close.iloc[-1] - low_52w) / (high_52w - low_52w) * 100

        # --- Volume trend ---
        avg_vol_20d = volume.tail(20).mean()
        avg_vol_60d = volume.tail(60).mean()
        volume_trend = (avg_vol_20d - avg_vol_60d) / avg_vol_60d * 100

        # --- Fundamentals ---
        pe_ratio = info.get("trailingPE", 25.0)
        if pe_ratio is None or pe_ratio != pe_ratio:  # NaN check
            pe_ratio = 25.0
        pe_ratio = min(pe_ratio, 200)  # cap extreme values

        debt_to_equity = info.get("debtToEquity", 50.0)
        if debt_to_equity is None or debt_to_equity != debt_to_equity:
            debt_to_equity = 50.0
        debt_to_equity = min(debt_to_equity, 500)

        profit_margin = info.get("profitMargins", 0.1)
        if profit_margin is None or profit_margin != profit_margin:
            profit_margin = 0.1

        return {
            "ticker": ticker,
            "mom_1m": round(float(mom_1m), 2),
            "mom_3m": round(float(mom_3m), 2),
            "mom_1y": round(float(mom_1y), 2),
            "volatility_20d": round(float(volatility_20d), 2),
            "rsi_14": round(float(rsi), 2),
            "position_52w": round(float(position_52w), 2),
            "volume_trend": round(float(volume_trend), 2),
            "pe_ratio": round(float(pe_ratio), 2),
            "debt_to_equity": round(float(debt_to_equity), 2),
            "profit_margin": round(float(profit_margin), 4),
        }

    except Exception as e:
        return {"error": str(e)}