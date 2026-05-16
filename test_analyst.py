# test_analyst.py
from agents.analyst_agent import AnalystAgent

agent = AnalystAgent()

for ticker in ["AAPL", "MSFT", "NVDA"]:
    print(f"\n{'='*50}")
    print(f"ANALYST REPORT — {ticker}")
    print(f"{'='*50}")
    result = agent.run(ticker)
    print(f"Risk Score : {round(result['risk_score'], 1)}/100 ({result['risk_label']})")
    print(f"Top Factors:")
    for f in result["top_factors"]:
        print(f"  {f['factor']}: {f['shap_value']}")
    print(f"\nExplanation:\n{result['explanation']}")
    print(f"\nSHAP chart generated: {'✅' if result['shap_chart_b64'] else '❌'}")