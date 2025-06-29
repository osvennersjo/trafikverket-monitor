#!/usr/bin/env python3
import os
import sys

# Set the API key
os.environ['GEMINI_API_KEY'] = "AIzaSyAOYbQD5dAAQsYyK4lfFp-ciiXJgj3prCw"

# Import our system
from fixed_optimized_query_system import LLMCaller, LLMPromptGenerator

# Test the LLMCaller directly
print("Testing Gemini integration...")

# Create a simple prompt
test_prompt = """You are an expert ski equipment advisor providing accurate, helpful advice to skiers. Answer the user's specific question about this ski product.

USER QUESTION: What is the waist width of Atomic Bent 110?

PRODUCT DATA:
PRODUCT: Atomic Bent 110 24/25
Brand: atomic
Waist Width: 110.0mm
Price: 8000 SEK (usually), 7000 SEK (discounted)
Available Lengths: 172, 180, 188cm
Twin-tip: No

INSTRUCTIONS:
- Answer the specific question directly and accurately
- Use the exact data provided - don't make up specifications
- If asked about price, mention both regular and discounted prices if available
- If data is missing for what they asked, say so clearly
- Keep response concise and factual
- Include the product name in your response

RESPONSE:"""

print("Testing LLMCaller.call_gemini()...")
result = LLMCaller.call_gemini(test_prompt, max_tokens=200)

if result:
    print("✅ Gemini API working!")
    print(f"Response: {result}")
else:
    print("❌ Gemini API failed - using fallback")

print("\nTesting LLMCaller.call_openai() (compatibility method)...")
result2 = LLMCaller.call_openai(test_prompt, max_tokens=200)

if result2:
    print("✅ Compatibility method working!")
    print(f"Response: {result2}")
else:
    print("❌ Compatibility method failed") 