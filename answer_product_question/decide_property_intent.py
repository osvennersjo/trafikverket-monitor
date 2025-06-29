#!/usr/bin/env python3
"""
Property Intent Classifier

This script takes a query that has been proven by user_intent_final to be a property query
and determines if it is asking to compare, describe, or is a general question.
Uses the Google Gemini API with the same API key configuration as the rest of the project.
"""

import os
import sys
import logging
from typing import Literal, Optional, Tuple
import google.generativeai as genai  # type: ignore
import re

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

# --- Property Intent Classification Logic ---

def classify_property_intent_gemini(query: str, api_key: str) -> Optional[Literal["compare", "describe", "general"]]:
    """
    Classify a property query using the Gemini API.
    
    Args:
        query: A query that has been proven to be a property query
        api_key: Google Gemini API key
        
    Returns:
        "compare" if asking to compare products
        "describe" if asking about properties without comparison
        "general" if asking general questions about properties
        None if API call fails
    """
    logger.info(f"Attempting to classify property intent via Gemini: \"{query}\"")
    is_valid, error_message = validate_api_key_format(api_key)
    if not is_valid:
        logger.error(f"API key validation failed: {error_message}")
        return None

    try:
        # Configure the Gemini API with the key
        genai.configure(api_key=api_key)
        
        # Define the classification prompt
        prompt = f"""
        You are classifying property queries into three categories:

        1. "compare" - The query asks to compare two or more different products in any regard.
           Key indicators: "which", "or", "vs", "versus", "between", "better", "worse", "comparing"
           Examples: 
           - "Which is better, these skis or those skis?"
           - "Compare the waterproofing of these two jackets"
           - "Are these boots warmer than those boots?"
           - "Which camera has better image quality?"
           - "Which is best for skiing in deep powder, Head Oblivion Jr 24/25 or DPS Carbon Wailer 107 24/25?"
           - "For aggressive charging, Völkl Mantra 88 25/26 or Nordica Enforcer 93 24/25?"
           - "Between Fischer Nightstick 97 24/25 and Line Pandora 106 24/25, which is more agile?"
           - "Should I choose Armada ARV 112 24/25 or Blizzard Rustler 10 24/25 for freestyle?"
           - "For park performance, Line Honey Badger or Armada ARV 86?"
           - "Rossignol vs Atomic for beginners?"

        2. "describe" - The query asks about properties of ONE specific product without comparison.
           Examples:
           - "Is this waterproof?"
           - "Does this camera have image stabilization?"
           - "What material is this jacket made of?"
           - "Can I use the Black Diamond Impulse Ti 98 for off-piste?"
           - "Will the Atomic Maverick 105 CTi work well in icy conditions?"
           - "Is the Faction Studio Grom suitable for high-speed carving?"
           - "How stable is the Nordica Enforcer 93 at high speeds?"

        3. "general" - The query is a general question about properties or requirements, NOT about specific products.
           Examples:
           - "Do I need waterproof shoes for hiking?"
           - "What should I think about before skiing off-piste?"
           - "What makes a good winter jacket?"
           - "How important is lens quality in cameras?"

        CRITICAL RULES:
        - Pattern "For [purpose], [Product A] or [Product B]?" is ALWAYS "compare"
        - If the query mentions TWO OR MORE specific product names/models → "compare"
        - If the query uses "or" between products → "compare"
        - If the query starts with "Which" followed by product names → "compare"
        - If the query mentions only ONE specific product → "describe"
        - If no specific products are mentioned → "general"

        Respond with ONLY one word: "compare", "describe", or "general"

        Query: {query}
        Classification:
        """

        # Use Gemini API to generate a response
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        # Extract and parse the result
        result = response.text.strip().lower()
        
        if "compare" in result:
            return "compare"
        elif "describe" in result:
            return "describe"
        elif "general" in result:
            return "general"
        
        logger.warning(f"Unexpected response from Gemini: {result}. Defaulting to describe.")
        return "describe"
    
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return None

def classify_property_intent_rules_based(query: str) -> Literal["compare", "describe", "general"]:
    """
    A rule-based fallback classifier for property intent.
    
    Args:
        query: A query that has been proven to be a property query
        
    Returns:
        "compare", "describe", or "general"
    """
    lower_query = query.lower()
    
    # Strong comparison indicators that almost always indicate comparison
    strong_compare_indicators = [
        "which is better", "which is best", "which is more", "which has",
        "which offers", "which would", "which ski", "which camera", "which product",
        "comparing", "compared to", "versus", " vs ", "between",
        "should i pick", "should i choose", "recommend for"
    ]
    
    # Check for strong comparison indicators first
    for indicator in strong_compare_indicators:
        if indicator in lower_query:
            logger.info("Classified as 'compare' by rules-based logic (strong comparison indicator).")
            return "compare"
    
    # Check for "For [purpose], X or Y?" pattern - always indicates comparison
    if lower_query.startswith("for ") and " or " in lower_query:
        # Extract the part after "for" to check if it contains product names
        after_for = lower_query[4:]  # Skip "for "
        comma_pos = after_for.find(",")
        if comma_pos > 0:
            # Check if there's an "or" after the comma  
            after_comma = after_for[comma_pos+1:].strip()
            if " or " in after_comma:
                logger.info("Classified as 'compare' by rules-based logic (For [purpose], X or Y pattern).")
                return "compare"
    
    # Check if query mentions multiple specific products (strong sign of comparison)
    # Count occurrences of model year patterns and brand names
    product_count = 0
    
    # Model year patterns
    year_patterns = re.findall(r'\d{2}/\d{2}', lower_query)
    product_count += len(set(year_patterns))  # Count unique year patterns
    
    # Check for " or " between products (e.g., "Product A or Product B")
    # But not for conditions like "powder or hardpack"
    if " or " in lower_query and product_count > 0:
        # Check if "or" is between product names, not conditions
        or_index = lower_query.find(" or ")
        before_or = lower_query[:or_index].split()[-2:] if or_index > 0 else []
        after_or = lower_query[or_index+4:].split()[:2] if or_index < len(lower_query) - 4 else []
        
        # Common condition words that shouldn't trigger comparison
        condition_words = ["powder", "hardpack", "ice", "groomed", "piste", "offpiste", 
                          "park", "carving", "touring", "moguls", "crud", "slush"]
        
        # Check if the words around "or" are conditions rather than products
        is_condition_or = any(word in condition_words for word in before_or + after_or)
        
        if not is_condition_or:
            logger.info("Classified as 'compare' by rules-based logic (products with 'or').")
            return "compare"
    
    # Check for specific product indicators (brands, model numbers, etc.)
    product_indicators = [
        # Brand names
        'atomic', 'armada', 'black diamond', 'blizzard', 'dynafit', 'faction',
        'fischer', 'head', 'k2', 'line', 'nordica', 'rossignol', 'salomon',
        'scott', 'volkl', 'völkl', 'dps', 'movement', 'elan'
    ]
    
    # Count distinct products mentioned
    mentioned_products = []
    for brand in product_indicators:
        if brand in lower_query:
            # Find all occurrences with their positions
            start = 0
            while True:
                pos = lower_query.find(brand, start)
                if pos == -1:
                    break
                mentioned_products.append((brand, pos))
                start = pos + 1
    
    # If multiple distinct products are mentioned, likely a comparison
    if len(mentioned_products) >= 2:
        # Check if there are comparison words anywhere in the query
        compare_words = ["better", "worse", "more", "less", "prefer", "recommend"]
        if any(word in lower_query for word in compare_words):
            logger.info("Classified as 'compare' by rules-based logic (multiple products with comparison words).")
            return "compare"
    
    # General question indicators
    general_indicators = [
        "do i need", "should i", "what should", "how important", "why do",
        "what makes", "how to choose", "what to look for", "is it worth",
        "do you recommend", "what about", "how much", "when should"
    ]
    
    # Check for general questions (but not if specific products are mentioned)
    has_specific_product = any(brand in lower_query for brand in product_indicators) or bool(year_patterns)
    
    if any(indicator in lower_query for indicator in general_indicators) and not has_specific_product:
        logger.info("Classified as 'general' by rules-based logic.")
        return "general"
    
    # Additional comparison patterns
    if any(pattern in lower_query for pattern in ["than", "versus", "compared to", "vs"]):
        logger.info("Classified as 'compare' by rules-based logic (comparison pattern).")
        return "compare"
    
    # Default classification
    if has_specific_product:
        logger.info("Classified as 'describe' by rules-based logic (specific product mentioned).")
        return "describe"
    else:
        logger.info("Classified as 'general' by rules-based logic (no specific products).")
        return "general"

def decide_property_intent(query: str) -> str:
    """
    Main function to determine property intent.
    
    Args:
        query: A query that has been proven to be a property query
        
    Returns:
        Formatted string: "query=property;compare", "query=property;describe", or "query=property;general"
    """
    api_key = get_api_key()
    
    # Try Gemini classification first
    classification = classify_property_intent_gemini(query, api_key)
    
    # Fall back to rules-based if Gemini fails
    if classification is None:
        logger.warning("Gemini classification failed. Falling back to rules-based classification.")
        classification = classify_property_intent_rules_based(query)
    
    # Format the output as requested
    result = f"query=property;{classification}"
    logger.info(f"Final classification: {result}")
    return result

# --- Main Execution ---
def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Classify property query intent into compare, describe, or general categories."
    )
    parser.add_argument("query", help="The property query to classify")
    
    args = parser.parse_args()
    
    result = decide_property_intent(args.query)
    print(result)

if __name__ == "__main__":
    main() 