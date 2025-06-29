#!/usr/bin/env python3
import os
import sys

# Set the API key exactly like in the server
os.environ['GEMINI_API_KEY'] = "AIzaSyAOYbQD5dAAQsYyK4lfFp-ciiXJgj3prCw"

# Import our system
from fixed_optimized_query_system import LLMCaller, LLMPromptGenerator, GEMINI_API_KEY, GEMINI_AVAILABLE

print(f"GEMINI_API_KEY set: {GEMINI_API_KEY is not None}")
print(f"GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
print(f"API Key from env: {os.getenv('GEMINI_API_KEY') is not None}")

# Test the LLM call directly
test_prompt = """You are an expert ski equipment advisor. Answer this question:

What is the waist width of Atomic Bent 110?

PRODUCT DATA:
PRODUCT: Atomic Bent 110 24/25
Brand: atomic
Waist Width: 110.0mm
Price: 8000 SEK (usually), 7000 SEK (discounted)

RESPONSE:"""

print("\nTesting LLM call...")
result = LLMCaller.call_gemini(test_prompt, max_tokens=200)

if result:
    print("✅ LLM call successful!")
    print(f"Response: {result}")
else:
    print("❌ LLM call failed")

# Also test the compatibility method
print("\nTesting compatibility method...")
result2 = LLMCaller.call_openai(test_prompt, max_tokens=200)

if result2:
    print("✅ Compatibility method successful!")
    print(f"Response: {result2}")
else:
    print("❌ Compatibility method failed") 