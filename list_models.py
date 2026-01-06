import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    with open("available_models.txt", "w") as f:
        f.write("Listing available models:\n")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"- {m.name}\n")
    print("✅ Full model list written to available_models.txt")
except Exception as e:
    print(f"Error listing models: {e}")
