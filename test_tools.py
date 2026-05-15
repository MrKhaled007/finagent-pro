# test_tools.py
import json
from tools.stock_data import get_stock_data
from tools.financials import get_financials
from tools.news import get_news

ticker = "AAPL"

print("=" * 50)
print(f"Testing all 3 tools on {ticker}")
print("=" * 50)

print("\n📈 STOCK DATA:")
stock = get_stock_data(ticker)
print(json.dumps(stock, indent=2, default=str))

print("\n💰 FINANCIALS:")
fins = get_financials(ticker)
print(json.dumps(fins, indent=2, default=str))

print("\n📰 NEWS:")
news = get_news(ticker)
for i, a in enumerate(news.get("articles", []), 1):
    print(f"\n  Article {i}: {a['title']}")
    print(f"  Sentiment: {a['sentiment']} ({a['sentiment_score']})")
print(f"\n  Avg sentiment score: {news.get('avg_sentiment_score')}")