# orchestrator.py
from agents.research_agent import ResearchAgent

research_agent = ResearchAgent()

def run_pipeline(ticker: str) -> dict:
    print(f"\n{'='*50}")
    print(f"Running pipeline for {ticker}")
    print(f"{'='*50}")

    result = research_agent.run(ticker)

    if "error" in result:
        print(f"[orchestrator] Pipeline failed: {result['error']}")
        return result

    print(f"[orchestrator] Pipeline complete for {ticker}")
    return result

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    result = run_pipeline(ticker)
    print("\n--- BRIEF ---")
    print(result["brief"])