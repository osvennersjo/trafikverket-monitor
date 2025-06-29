#!/usr/bin/env python3
import os
import google.generativeai as genai

# Set API key
api_key = "AIzaSyAOYbQD5dAAQsYyK4lfFp-ciiXJgj3prCw"
genai.configure(api_key=api_key)

# List available models
try:
    print("Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
    
    # Test with the correct model name
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("What is 2+2? Give a very short answer.")
    print("\n✅ Gemini API working!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Gemini API error: {e}") 