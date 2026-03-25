import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API key found in .env")
    exit(1)

client = genai.Client(api_key=api_key)

print("Available Models:")
try:
    for m in client.models.list():
        print(f"- {m.name}: {getattr(m, 'supported_generation_methods', 'UNKNOWN')}")
except Exception as e:
    print(f"Failed to list models: {e}")
