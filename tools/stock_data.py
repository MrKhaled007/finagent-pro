# tools/stock_data.py
import yfinance as yf

def get_stock_data(ticker: str) -> dict:
    """Fetch 1Y OHLCV history + current price info for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        info = stock.info

        if hist.empty:
            return {"error": f"No price data found for {ticker}"}

        # Calculate basic metrics
        current_price = hist["Close"].iloc[-1]
        price_1m_ago = hist["Close"].iloc[-22] if len(hist) > 22 else hist["Close"].iloc[0]
        price_3m_ago = hist["Close"].iloc[-66] if len(hist) > 66 else hist["Close"].iloc[0]
        price_1y_ago = hist["Close"].iloc[0]

        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "change_1m_pct": round((current_price - price_1m_ago) / price_1m_ago * 100, 2),
            "change_3m_pct": round((current_price - price_3m_ago) / price_3m_ago * 100, 2),
            "change_1y_pct": round((current_price - price_1y_ago) / price_1y_ago * 100, 2),
            "52w_high": round(hist["Close"].max(), 2),
            "52w_low": round(hist["Close"].min(), 2),
            "avg_volume": int(hist["Volume"].mean()),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "history_closes": hist["Close"].tail(30).round(2).tolist(),
        }
    except Exception as e:
        return {"error": str(e)}