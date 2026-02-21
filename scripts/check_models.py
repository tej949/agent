import os
import traceback
from dotenv import load_dotenv

load_dotenv()
print("GOOGLE_API_KEY=", os.getenv("GOOGLE_API_KEY"))

try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    models = client.models.list()
    print("Models:")
    for m in models:
        print("-", getattr(m, "name", str(m)))
except Exception:
    traceback.print_exc()
