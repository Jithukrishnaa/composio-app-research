import os
from dotenv import load_dotenv

load_dotenv()

COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not COMPOSIO_API_KEY:
    print("WARNING: COMPOSIO_API_KEY is not configured.")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not configured.")