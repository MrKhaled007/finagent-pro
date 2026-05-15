# test_research.py
from agents.research_agent import ResearchAgent

agent = ResearchAgent()
result = agent.run("AAPL")

print(f"\n{'='*50}")
print(f"RESEARCH BRIEF — {result['ticker']}")
print(f"Price: ${result['current_price']} | 1Y: {result['change_1y_pct']}% | PE: {result['pe_ratio']}")
print(f"{'='*50}")
print(result["brief"])