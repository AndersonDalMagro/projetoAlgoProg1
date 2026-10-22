import google.generativeai as genai
from my_keys import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name.replace("models/", ""))
