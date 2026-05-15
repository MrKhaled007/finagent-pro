# tools/financials.py
import yfinance as yf

def get_financials(ticker: str) -> dict:
    """Fetch income statement + balance sheet key metrics."""
    try:
        stock = yf.Ticker(ticker)
        income = stock.income_stmt
        balance = stock.balance_sheet

        if income is None or income.empty:
            return {"error": f"No financial data for {ticker}"}

        # Get most recent year column
        latest = income.columns[0]

        def safe_get(df, row):
            try:
                val = df.loc[row, latest]
                return int(val) if str(val) != "nan" else "N/A"
            except:
                return "N/A"

        return {
            "ticker": ticker,
            "period": str(latest.date()),
            "total_revenue": safe_get(income, "Total Revenue"),
            "gross_profit": safe_get(income, "Gross Profit"),
            "operating_income": safe_get(income, "Operating Income"),
            "net_income": safe_get(income, "Net Income"),
            "total_assets": safe_get(balance, "Total Assets"),
            "total_debt": safe_get(balance, "Total Debt"),
            "cash": safe_get(balance, "Cash And Cash Equivalents"),
            "stockholders_equity": safe_get(balance, "Stockholders Equity"),
        }
    except Exception as e:
        return {"error": str(e)}