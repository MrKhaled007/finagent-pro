# agents/research_agent.py
from agents.base_agent import BaseAgent
from tools.stock_data import get_stock_data
from tools.financials import get_financials
from tools.news import get_news

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("research")

    def run(self, ticker: str) -> dict:
        print(f"[research] Fetching data for {ticker}...")

        stock = get_stock_data(ticker)
        fins = get_financials(ticker)
        news = get_news(ticker)

        if "error" in stock:
            return {"error": f"Stock data failed: {stock['error']}"}

        prompt = f"""
You are a professional equity research analyst. Based on the following data, write a structured research brief for {ticker}.

--- PRICE DATA ---
Current Price: ${stock['current_price']}
1-Month Change: {stock['change_1m_pct']}%
3-Month Change: {stock['change_3m_pct']}%
1-Year Change: {stock['change_1y_pct']}%
52-Week High: ${stock['52w_high']}
52-Week Low: ${stock['52w_low']}
P/E Ratio: {stock['pe_ratio']}
Sector: {stock['sector']}

--- FINANCIALS (most recent year) ---
Revenue: ${fins.get('total_revenue', 'N/A'):,}
Gross Profit: ${fins.get('gross_profit', 'N/A'):,}
Operating Income: ${fins.get('operating_income', 'N/A'):,}
Net Income: ${fins.get('net_income', 'N/A'):,}
Total Debt: ${fins.get('total_debt', 'N/A'):,}
Cash: ${fins.get('cash', 'N/A'):,}

--- RECENT NEWS ---
{self._format_news(news)}

Write a structured brief with exactly these 4 sections:
1. PRICE TREND: Summarise price momentum and where the stock sits vs its 52-week range.
2. FINANCIAL HEALTH: Summarise revenue, profitability, debt load, and cash position.
3. NEWS SENTIMENT: Summarise the news themes and their likely market impact.
4. KEY RISKS: List the top 3 specific risks based on the data above.

Be concise, data-driven, and professional. Each section 3-5 sentences max.
"""
        print(f"[research] Calling Gemini for analysis...")
        brief = self.call_gemini(prompt)

        return {
            "ticker": ticker,
            "current_price": stock["current_price"],
            "change_1y_pct": stock["change_1y_pct"],
            "pe_ratio": stock["pe_ratio"],
            "sector": stock["sector"],
            "avg_sentiment_score": news.get("avg_sentiment_score", 0),
            "brief": brief,
            "raw_stock": stock,
            "raw_fins": fins,
            "raw_news": news,
        }

    def _format_news(self, news: dict) -> str:
        articles = news.get("articles", [])
        if not articles:
            return "No recent news available."
        lines = []
        for a in articles:
            lines.append(f"- {a['title']} [{a['sentiment']}]")
        return "\n".join(lines)