import google.generativeai as genai
import os

# Replace 'YOUR_API_KEY' with your actual Gemini API key
# Or set it as an environment variable
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"

def list_available_models():
    """
    Lists all available Gemini models for the current API key.
    """
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    print("Checking available Gemini models...\n")
    
    try:
        # Fetch the list of models
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model Name: {m.name}")
                print(f"Display Name: {m.display_name}")
                print(f"Description: {m.description}")
                print("-" * 30)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_available_models()
    