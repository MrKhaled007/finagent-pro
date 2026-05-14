import sys
sys.path.insert(0, '.')
from agents.base_agent import BaseAgent

agent = BaseAgent("test")
response = agent.call_gemini("Say hello and confirm you are Gemini. Keep it to one sentence.")
print("✅ Gemini response:", response)