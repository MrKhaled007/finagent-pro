# tools/news.py
import requests
from config import ALPHA_VANTAGE_KEY

def get_news(ticker: str, limit: int = 5) -> dict:
    """Fetch latest news headlines for a ticker via Alpha Vantage."""
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "limit": limit,
            "apikey": ALPHA_VANTAGE_KEY,
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "feed" not in data:
            return {"error": f"No news data returned for {ticker}", "raw": data}

        articles = []
        for item in data["feed"][:limit]:
            articles.append({
                "title": item.get("title", ""),
                "summary": item.get("summary", "")[:300],
                "source": item.get("source", ""),
                "published": item.get("time_published", ""),
                "sentiment": item.get("overall_sentiment_label", ""),
                "sentiment_score": item.get("overall_sentiment_score", 0),
            })

        return {
            "ticker": ticker,
            "articles": articles,
            "avg_sentiment_score": round(
                sum(a["sentiment_score"] for a in articles) / len(articles), 3
            ) if articles else 0,
        }
    except Exception as e:
        return {"error": str(e)}