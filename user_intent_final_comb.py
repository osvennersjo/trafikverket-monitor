#!/usr/bin/env python3
"""
User Intent Final Classifier (Combined & Standalone)

This script classifies user queries as 'search query' or 'property query'
using the Google Gemini API. It is designed to be self-contained and includes API key setup.
"""

import os
import sys
import logging
import argparse
from typing import Literal, Optional, Tuple
import google.generativeai as genai # type: ignore

# --- Configuration ---
# This key will be used if GOOGLE_API_KEY environment variable is not set.
# IMPORTANT: For security, it's better to use an environment variable.
FALLBACK_API_KEY = "AIzaSyAOYbQD5dAAQsYyK4lfFp-ciiXJgj3prCw"
ENV_FILE_NAME = ".env"
ENV_VAR_NAME = "GOOGLE_API_KEY"  # Name of the environment variable
# --- End Configuration ---

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- API Key Management --- 
def get_api_key_from_env_file() -> Optional[str]:
    """Reads the API key from the .env file if it exists."""
    env_path = os.path.join(os.getcwd(), ENV_FILE_NAME)
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith(f"{ENV_VAR_NAME}="):
                    key = line.split("=", 1)[1].strip()
                    if key:
                        return key
    return None

def get_api_key() -> str:
    """Retrieves the API key, preferring environment variable, then .env file, then fallback."""
    env_var_api_key = os.getenv(ENV_VAR_NAME)
    if env_var_api_key:
        logger.info(f"Using Gemini API key from {ENV_VAR_NAME} environment variable.")
        return env_var_api_key
    
    env_file_api_key = get_api_key_from_env_file()
    if env_file_api_key:
        logger.info(f"Using Gemini API key from {ENV_FILE_NAME} file.")
        return env_file_api_key

    logger.warning(f"Using fallback API key. Consider setting {ENV_VAR_NAME} environment variable or in {ENV_FILE_NAME}.")
    return FALLBACK_API_KEY

def validate_api_key_format(api_key: str) -> Tuple[bool, str]:
    """
    Validate that the API key is set and properly formatted.
    Returns: Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "Google API key not found."
    if not api_key.startswith("AIza"):
        return False, "Invalid API key format. Google Gemini API keys typically start with 'AIza'."
    if len(api_key) < 30:  # Gemini keys are typically long
        return False, "API key appears too short. Please check its validity."
    return True, ""

def update_env_file_with_key(api_key: str) -> bool:
    """Update the .env file with the new API key or create it if it doesn't exist."""
    env_path = os.path.join(os.getcwd(), ENV_FILE_NAME)
    new_lines = []
    key_updated = False

    required_vars = {
        "FLASK_ENV": "development",
        "SECRET_KEY": "your-default-secret-key", # Consider generating a random one
        "PORT": "5000"
    }

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith(f"{ENV_VAR_NAME}="):
                new_lines.append(f"{ENV_VAR_NAME}={api_key}\n")
                key_updated = True
            else:
                new_lines.append(line)
                var_name = line.split("=",1)[0]
                if var_name in required_vars:
                    del required_vars[var_name]
    
    if not key_updated:
        new_lines.append(f"{ENV_VAR_NAME}={api_key}\n")
    
    for var, val in required_vars.items():
        new_lines.append(f"{var}={val}\n")

    try:
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        logger.info(f"Successfully updated/created {ENV_FILE_NAME} with the API key.")
        return True
    except IOError as e:
        logger.error(f"Failed to write to {ENV_FILE_NAME}: {e}")
        return False

# --- Intent Classification Logic ---

def classify_query_gemini(query: str, api_key: str) -> Optional[Literal["search query", "property query"]]:
    """ Classify a user query using the Gemini API. """
    logger.info(f"Attempting to classify query via Gemini: \"{query}\"")
    is_valid, error_message = validate_api_key_format(api_key)
    if not is_valid:
        logger.error(f"API key validation failed: {error_message}")
        return None

    try:
        # Configure the Gemini API with the key
        genai.configure(api_key=api_key)
        
        # Define the classification prompt
        prompt = f"""
        Classify the following query as either a "search query" or a "property query".

        DEFINITIONS:
        
        "search query" = Looking for product recommendations or searching for products that meet certain criteria
        - User wants to discover/find specific products to buy
        - Asking for product recommendations or lists
        - Examples:
          • "What are the best skis for beginners?" (wants specific product recommendations)
          • "Show me lightweight touring skis" (wants to see products)
          • "Find skis under $500" (wants product list)
          • "Recommend a camera for wildlife photography" (wants recommendations)
          • "What products do you have for powder skiing?" (wants to browse products)

        "property query" = Asking about characteristics, properties, features, or comparisons
        - Questions about product properties/characteristics (general or specific)
        - Questions about whether certain features are needed/important
        - Questions about the purpose or benefit of features
        - Comparisons between products or features
        - Examples:
          • "Is the Völkl Mantra 88 good for powder?" (specific product property)
          • "Can the Atomic Maverick handle icy conditions?" (specific product capability)
          • "Which is better, Rossignol or Line skis for park?" (comparison)
          • "Do I need special bindings for touring skis?" (general property question)
          • "What makes a ski good for carving?" (general characteristic question)
          • "How important is ski stiffness for beginners?" (property importance)
          • "Should I get twin-tip skis for all-mountain skiing?" (property advice)
          • "Is waterproofing necessary for ski gear?" (property necessity)
          • "Do wider skis make a difference?" (property impact)
          • "What's the point of rocker technology?" (property purpose)

        IMPORTANT RULES:
        1. If the query mentions ANY specific product names/models → "property query"
        2. If the query asks to compare specific items → "property query"
        3. If the query asks about general product characteristics → "property query"
        4. Questions with "Should I get...", "Do I need...", "Is ... necessary", "What's the point of..." are asking about properties → "property query"
        5. Only classify as "search query" if explicitly asking for product recommendations or lists to choose from
        6. When in doubt, lean towards "property query"

        Your response should be EXACTLY one of these two phrases: "search query" or "property query"

        Query: {query}
        Classification:
        """

        # Use Gemini API to generate a response
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        # Extract and parse the result
        result = response.text.strip().lower()
        if "search query" in result: return "search query"
        if "property query" in result: return "property query"
        
        logger.warning(f"Unexpected response from Gemini: {result}. Defaulting to search query.")
        return "search query"
    
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return None

def classify_query_rules_based(query: str) -> Literal["search query", "property query"]:
    """A simple rule-based fallback classifier."""
    lower_query = query.lower()
    
    # Property query indicators - expanded list
    property_indicators = [
        # Specific product mentions
        "this", "these", "the specific", 
        # Question forms about properties
        "does it", "can it", "is it", "will it", "how does",
        # Comparison patterns
        "which is better", "which is best", " or ", " vs ", "versus", "compare",
        # General property questions - EXPANDED
        "do i need", "what makes", "how important", "what should i look for",
        "should i get", "should i buy", "is it worth", "is it necessary",
        "what's the point", "what is the purpose", "why use", "why do",
        "do wider", "does", "make a difference", "matter",
        # Additional property indicators
        "suitable for", "good for", "handle", "work well", "stable at",
        "necessary", "important", "worth getting"
    ]
    
    # Search query indicators - more restrictive
    search_indicators = [
        "what are the best", "show me", "find me", "recommend me", "looking for",
        "what products", "what options", "list of", "catalog", "browse",
        "suggestions for", "options for", "give me recommendations"
    ]
    
    # Check for brand names (strong indicator of property query)
    ski_brands = ['atomic', 'armada', 'black diamond', 'blizzard', 'faction', 'fischer', 
                  'head', 'k2', 'line', 'nordica', 'rossignol', 'salomon', 'volkl', 'völkl',
                  'dps', 'black crows', 'moment', 'dynastar', 'movement']
    has_brand = any(brand in lower_query for brand in ski_brands)
    
    # Check for model year patterns (e.g., "24/25", "25/26")
    import re
    has_model_year = bool(re.search(r'\d{2}/\d{2}', query))
    
    # If query mentions specific brands/products or model years, it's likely a property query
    if has_brand or has_model_year:
        logger.info("Classified as 'property query' by rules-based logic (brand/model mentioned).")
        return "property query"
    
    # Special patterns that are definitely property queries
    property_patterns = [
        r"should i (get|buy)",
        r"do i need",
        r"is .* necessary",
        r"what('s| is) the (point|purpose)",
        r"do .* make a difference",
        r"is .* worth",
        r"how important"
    ]
    
    for pattern in property_patterns:
        if re.search(pattern, lower_query):
            logger.info(f"Classified as 'property query' by rules-based logic (pattern: {pattern}).")
            return "property query"
    
    # Check for property indicators
    if any(indicator in lower_query for indicator in property_indicators):
        # Make sure it's not a clear search query
        if not any(s_ind in lower_query for s_ind in search_indicators):
            logger.info("Classified as 'property query' by rules-based logic.")
            return "property query"
    
    # Check for search indicators
    if any(indicator in lower_query for indicator in search_indicators):
        logger.info("Classified as 'search query' by rules-based logic.")
        return "search query"
    
    # Check for general property questions (questions about characteristics without specific products)
    general_property_patterns = [
        "what makes", "how important", "why do", "what should", "do i need",
        "what's the difference", "what does", "explain", "tell me about"
    ]
    if any(pattern in lower_query for pattern in general_property_patterns):
        logger.info("Classified as 'property query' by rules-based logic (general property question).")
        return "property query"
    
    # Default to property query if it's a question
    if "?" in query and not any(s_ind in lower_query for s_ind in search_indicators):
        logger.info("Classified as 'property query' by rules-based logic (question without search indicators).")
        return "property query"
    
    # Default to search query only if no property indicators found
    logger.info("No clear indicators found, defaulting to search query.")
    return "search query"

def get_intent(query: str, current_api_key: str) -> str:
    """Determines user intent, trying Gemini first, then rules-based fallback."""
    classification = classify_query_gemini(query, current_api_key)
    if classification is None:
        logger.warning("Gemini classification failed. Falling back to rules-based classification.")
        classification = classify_query_rules_based(query)
    return classification

# --- Main Execution & CLI --- 
def main_cli():
    """Command line interface for the user intent classifier, including API key setup."""
    parser = argparse.ArgumentParser(
        description="Classify user query intent. Can also set/check API key.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("query", nargs="?", help="The query text to classify. If omitted, prompts interactively.")
    parser.add_argument(
        "--set-api-key", 
        metavar='API_KEY', 
        nargs='?', # Optional argument for the key itself
        const="PROMPT", # Value if flag is present but no key given
        help=f"Set/update the Gemini API key in the {ENV_FILE_NAME} file. \n"
             "If API_KEY is provided, it's used. Otherwise, prompts for the key."
    )
    parser.add_argument("--check-api", action="store_true", help="Validate the current API key and exit.")

    args = parser.parse_args()
    active_api_key = get_api_key() # Get current effective API key

    if args.set_api_key:
        new_key_to_set = ""
        if args.set_api_key == "PROMPT":
            new_key_to_set = input("Enter your Gemini API key (starts with 'AIza'): ").strip()
        else:
            new_key_to_set = args.set_api_key.strip()
        
        is_valid, msg = validate_api_key_format(new_key_to_set)
        if not is_valid:
            print(f"❌ Error: {msg} Please provide a valid API key.")
            sys.exit(1)
        
        if update_env_file_with_key(new_key_to_set):
            print(f"✅ API key updated in {ENV_FILE_NAME}. The script will use this new key on next run if not overridden by env var.")
        else:
            print(f"❌ Failed to update {ENV_FILE_NAME}.")
        sys.exit(0)

    if args.check_api:
        is_valid, message = validate_api_key_format(active_api_key)
        print(f"Effective API Key Source: {(f'{ENV_VAR_NAME} env var' if os.getenv(ENV_VAR_NAME) else (f'{ENV_FILE_NAME} file' if get_api_key_from_env_file() else 'Fallback hardcoded key'))}")
        if is_valid:
            print(f"✅ API key ({active_api_key[:7]}...) validation successful.")
        else:
            print(f"❌ API key error: {message}")
        sys.exit(0 if is_valid else 1)

    query_text = args.query
    if not query_text:
        try:
            query_text = input("Enter your query (or type 'exit'): ").strip()
            if not query_text or query_text.lower() == 'exit':
                print("No query provided or exiting. Goodbye!")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\nExiting.")
            sys.exit(0)
            
    intent = get_intent(query_text, active_api_key)
    print(f"\nQuery: \"{query_text}\"")
    print(f"Intent: {intent}")
    print(f"\nResult: query = {intent}")

if __name__ == "__main__":
    # Ensure the google-generativeai package is available
    try:
        import google.generativeai
    except ImportError:
        print("Google Generative AI Python package is not installed. Please install it by running:")
        print("pip install google-generativeai")
        sys.exit(1)
    main_cli() 

