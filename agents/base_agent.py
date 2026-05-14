import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, TEMPERATURE, MAX_TOKENS

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"

    def call_gemini(self, prompt: str, retries: int = 3) -> str:
        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=TEMPERATURE,
                        max_output_tokens=MAX_TOKENS,
                    )
                )
                return response.text
            except Exception as e:
                if attempt < retries - 1:
                    wait = 2 ** attempt
                    print(f"[{self.name}] Retry {attempt+1} after error: {e}. Waiting {wait}s...")
                    time.sleep(wait)
                else:
                    raise RuntimeError(f"[{self.name}] Gemini call failed after {retries} attempts: {e}")