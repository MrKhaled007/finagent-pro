# orchestrator.py
import time
import json
from datetime import datetime, timezone
from agents.research_agent import ResearchAgent
from agents.analyst_agent import AnalystAgent

# Initialize agents once
research_agent = ResearchAgent()
analyst_agent = AnalystAgent()

def log_step(agent_name: str, ticker: str, status: str, duration: float, extra: dict = None):
    """Structured JSON log line — Cloud Logging will parse this automatically."""
    log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "ticker": ticker,
        "status": status,
        "duration_s": round(duration, 2),
    }
    if extra:
        log.update(extra)
    print(f"LOG: {json.dumps(log, default=str)}")

def run_pipeline(ticker: str) -> dict:
    pipeline_start = time.time()
    print(f"\n{'='*60}")
    print(f"🚀 Running FinAgent Pro pipeline for {ticker}")
    print(f"{'='*60}\n")

    result = {"ticker": ticker, "agents": {}, "errors": []}

    # --- Research Agent ---
    try:
        t0 = time.time()
        research = research_agent.run(ticker)
        duration = time.time() - t0
        if "error" in research:
            log_step("research", ticker, "error", duration, {"error": research["error"]})
            result["errors"].append({"agent": "research", "error": research["error"]})
            return result
        log_step("research", ticker, "ok", duration, {
            "sector": research.get("sector"),
            "price": research.get("current_price"),
        })
        result["agents"]["research"] = research
    except Exception as e:
        duration = time.time() - t0
        log_step("research", ticker, "exception", duration, {"error": str(e)})
        result["errors"].append({"agent": "research", "error": str(e)})
        return result

    # --- Analyst Agent ---
    try:
        t0 = time.time()
        analyst = analyst_agent.run(ticker, research_brief=research.get("brief", ""))
        duration = time.time() - t0
        if "error" in analyst:
            log_step("analyst", ticker, "error", duration, {"error": analyst["error"]})
            result["errors"].append({"agent": "analyst", "error": analyst["error"]})
            return result
        log_step("analyst", ticker, "ok", duration, {
            "risk_score": analyst.get("risk_score"),
            "risk_label": analyst.get("risk_label"),
        })
        result["agents"]["analyst"] = analyst
    except Exception as e:
        duration = time.time() - t0
        log_step("analyst", ticker, "exception", duration, {"error": str(e)})
        result["errors"].append({"agent": "analyst", "error": str(e)})
        return result

    # --- Pipeline complete ---
    total = time.time() - pipeline_start
    log_step("pipeline", ticker, "complete", total, {
        "risk_score": analyst.get("risk_score"),
        "risk_label": analyst.get("risk_label"),
    })

    result["summary"] = {
        "ticker": ticker,
        "current_price": research.get("current_price"),
        "change_1y_pct": research.get("change_1y_pct"),
        "sector": research.get("sector"),
        "risk_score": analyst.get("risk_score"),
        "risk_label": analyst.get("risk_label"),
        "top_risk_factors": [f["factor"] for f in analyst.get("top_factors", [])[:3]],
        "total_duration_s": round(total, 2),
    }

    return result

def save_shap_chart(result: dict, output_dir: str = "reports"):
    """Save SHAP chart from base64 to PNG for inspection."""
    import os, base64
    os.makedirs(output_dir, exist_ok=True)
    analyst = result.get("agents", {}).get("analyst", {})
    b64 = analyst.get("shap_chart_b64")
    if not b64:
        return None
    ticker = result["ticker"]
    path = f"{output_dir}/{ticker}_shap.png"
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    return path

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    result = run_pipeline(ticker)

    if result.get("errors"):
        print("\n❌ Pipeline had errors:")
        for e in result["errors"]:
            print(f"  - {e['agent']}: {e['error']}")
    else:
        s = result["summary"]
        print(f"\n{'='*60}")
        print(f"📊 SUMMARY — {s['ticker']}")
        print(f"{'='*60}")
        print(f"Price       : ${s['current_price']} ({s['change_1y_pct']:+.1f}% 1Y)")
        print(f"Sector      : {s['sector']}")
        print(f"Risk Score  : {round(s['risk_score'], 1)}/100 ({s['risk_label']})")
        print(f"Top Factors : {', '.join(s['top_risk_factors'])}")
        print(f"Total Time  : {s['total_duration_s']}s")

        chart_path = save_shap_chart(result)
        if chart_path:
            print(f"SHAP Chart  : {chart_path}")