import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

# Force utf-8 output (though writing to file shouldn't care about stdout)
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    with open("models.txt", "w", encoding="utf-8") as f:
        f.write("Error: GEMINI_API_KEY not found.")
else:
    genai.configure(api_key=api_key)
    try:
        with open("models.txt", "w", encoding="utf-8") as f:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(m.name + "\n")
        print("Done writing models.txt")
    except Exception as e:
        with open("models.txt", "w", encoding="utf-8") as f:
            f.write(f"Error: {e}")
