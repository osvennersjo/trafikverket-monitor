#!/usr/bin/env python3


"""
If Describing - Handler for Descriptive Property Queries

This file handles queries classified as "query=property;describe"
Descriptive queries ask about specific properties or characteristics of products.

Examples:
- "Will this work in offpiste?"
- "Is this good for beginners?"
- "How stable is this ski?"
- "Is this lightweight?"

The handler transforms queries into intent tags with flex ratings (0-1) and uses
Gemini to translate these into human-readable responses.
"""

import os
import sys
import logging
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
FALLBACK_API_KEY = "AIzaSyAOYbQD5dAAQsYyK4lfFp-ciiXJgj3prCw"
CSV_FILE_PATH = "alpingaraget_ai_optimized.csv"

def get_api_key() -> str:
    """Get Gemini API key from environment or fallback."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        logger.info("Using Gemini API key from environment variable.")
        return api_key
    
    logger.warning("Using fallback API key.")
    return FALLBACK_API_KEY

def load_product_database() -> pd.DataFrame:
    """
    Load the Alpingaraget product database from AI-optimized CSV file.
    
    Returns:
        DataFrame with product information or empty DataFrame if file not found
    """
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        logger.info(f"Loaded {len(df)} products from AI-optimized database")
        return df
    except FileNotFoundError:
        logger.error(f"Database file not found: {CSV_FILE_PATH}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading database: {e}")
        return pd.DataFrame()

def extract_intent_tags(query: str) -> Dict[str, float]:
    """
    Extract user intent tags from the query and assign flex ratings (0-1).
    
    Args:
        query: The user's descriptive query
        
    Returns:
        Dictionary of intent tags with their flex ratings
    """
    query_lower = query.lower()
    intent_tags = {}
    
    # Function/Usage Intent Tags
    if any(word in query_lower for word in ['offpiste', 'off-piste', 'off piste', 'powder', 'deep snow']):
        intent_tags['function_offpiste'] = 0.9
    
    if any(word in query_lower for word in ['piste', 'groomed', 'prepared', 'carving']):
        intent_tags['function_piste'] = 0.9
    
    if any(word in query_lower for word in ['park', 'freestyle', 'jibbing', 'rails', 'jumps']):
        intent_tags['function_park'] = 0.9
    
    if any(word in query_lower for word in ['all-mountain', 'allmountain', 'versatile', 'all mountain']):
        intent_tags['function_allmountain'] = 0.9
    
    if any(word in query_lower for word in ['touring', 'backcountry', 'uphill', 'skinning']):
        intent_tags['function_touring'] = 0.9
    
    if any(word in query_lower for word in ['freeride', 'big mountain', 'steep']):
        intent_tags['function_freeride'] = 0.9
    
    # Skill Level Intent Tags
    if any(word in query_lower for word in ['beginner', 'new', 'learning', 'first time', 'easy']):
        intent_tags['skill_beginner'] = 0.9
    
    if any(word in query_lower for word in ['intermediate', 'medium', 'moderate']):
        intent_tags['skill_intermediate'] = 0.8
    
    if any(word in query_lower for word in ['advanced', 'expert', 'pro', 'aggressive']):
        intent_tags['skill_advanced'] = 0.9
    
    # Performance Characteristics Intent Tags
    if any(word in query_lower for word in ['stable', 'stability', 'steady']):
        intent_tags['performance_stability'] = 0.8
    
    if any(word in query_lower for word in ['lightweight', 'light', 'weight']):
        intent_tags['performance_weight'] = 0.8
    
    if any(word in query_lower for word in ['fast', 'speed', 'quick']):
        intent_tags['performance_speed'] = 0.8
    
    if any(word in query_lower for word in ['responsive', 'agile', 'nimble', 'maneuverable']):
        intent_tags['performance_responsiveness'] = 0.8
    
    if any(word in query_lower for word in ['forgiving', 'easy turn', 'smooth']):
        intent_tags['performance_forgiving'] = 0.8
    
    if any(word in query_lower for word in ['durable', 'strong', 'tough', 'lasting']):
        intent_tags['performance_durability'] = 0.7
    
    if any(word in query_lower for word in ['control', 'precise', 'precision']):
        intent_tags['performance_control'] = 0.8
    
    # Physical Characteristics Intent Tags
    if any(word in query_lower for word in ['wide', 'width', 'fat']):
        intent_tags['physical_width'] = 0.8
    
    if any(word in query_lower for word in ['narrow', 'thin', 'skinny']):
        intent_tags['physical_narrow'] = 0.8
    
    if any(word in query_lower for word in ['long', 'length']):
        intent_tags['physical_length'] = 0.7
    
    if any(word in query_lower for word in ['short', 'shorter']):
        intent_tags['physical_short'] = 0.7
    
    if any(word in query_lower for word in ['stiff', 'rigid']):
        intent_tags['physical_stiffness'] = 0.8
    
    if any(word in query_lower for word in ['flexible', 'soft', 'flex']):
        intent_tags['physical_flexibility'] = 0.8
    
    # Condition-specific Intent Tags
    if any(word in query_lower for word in ['ice', 'icy', 'hard pack', 'hardpack']):
        intent_tags['condition_ice'] = 0.9
    
    if any(word in query_lower for word in ['moguls', 'bumps']):
        intent_tags['condition_moguls'] = 0.9
    
    if any(word in query_lower for word in ['variable', 'mixed', 'changing']):
        intent_tags['condition_variable'] = 0.8
    
    # Gender/Age Intent Tags
    if any(word in query_lower for word in ['women', 'female', 'ladies']):
        intent_tags['demographic_women'] = 0.9
    
    if any(word in query_lower for word in ['junior', 'kids', 'youth', 'children']):
        intent_tags['demographic_junior'] = 0.9
    
    # Price/Value Intent Tags
    if any(word in query_lower for word in ['expensive', 'premium', 'high-end']):
        intent_tags['value_premium'] = 0.8
    
    if any(word in query_lower for word in ['cheap', 'budget', 'affordable', 'value']):
        intent_tags['value_budget'] = 0.8
    
    return intent_tags

def analyze_product_match(intent_tags: Dict[str, float], df: pd.DataFrame) -> Dict[str, float]:
    """
    Analyze how well products in the database match the intent tags.
    
    Args:
        intent_tags: Dictionary of intent tags with ratings
        df: Product database DataFrame
        
    Returns:
        Dictionary with analysis results and confidence scores
    """
    if df.empty or not intent_tags:
        return {}
    
    analysis = {}
    
    # Count products that match each intent
    for intent, rating in intent_tags.items():
        matching_products = 0
        total_products = len(df)
        
        # Map intent tags to database tags
        search_terms = []
        
        if 'offpiste' in intent:
            search_terms = ['off-piste', 'powder', 'freeride', 'backcountry']
        elif 'piste' in intent:
            search_terms = ['piste', 'groomed', 'carving', 'all-mountain']
        elif 'park' in intent:
            search_terms = ['park', 'freestyle', 'jibbing', 'rails']
        elif 'allmountain' in intent:
            search_terms = ['all-mountain', 'versatile']
        elif 'touring' in intent:
            search_terms = ['touring', 'backcountry', 'lightweight']
        elif 'freeride' in intent:
            search_terms = ['freeride', 'big-mountain', 'powder']
        elif 'beginner' in intent:
            search_terms = ['beginner', 'forgiving', 'easy']
        elif 'intermediate' in intent:
            search_terms = ['intermediate']
        elif 'advanced' in intent:
            search_terms = ['advanced', 'expert', 'aggressive']
        elif 'stability' in intent:
            search_terms = ['stable', 'stability', 'control']
        elif 'weight' in intent:
            search_terms = ['lightweight', 'light', 'carbon']
        elif 'speed' in intent:
            search_terms = ['speed', 'fast', 'race']
        elif 'responsiveness' in intent:
            search_terms = ['responsive', 'agile', 'nimble']
        elif 'forgiving' in intent:
            search_terms = ['forgiving', 'easy', 'smooth']
        elif 'durability' in intent:
            search_terms = ['durable', 'strong', 'titanal']
        elif 'control' in intent:
            search_terms = ['control', 'precise', 'edge']
        elif 'width' in intent:
            search_terms = ['wide', 'fat', '100-mm', '110-mm', '120-mm']
        elif 'narrow' in intent:
            search_terms = ['narrow', '80-mm', '85-mm', '90-mm']
        elif 'women' in intent:
            search_terms = ['women', 'female']
        elif 'junior' in intent:
            search_terms = ['junior', 'youth', 'kids']
        
        # Count matching products
        for _, product in df.iterrows():
            tags_str = str(product.get('tags', ''))
            category_str = str(product.get('category', ''))
            
            if any(term in tags_str.lower() or term in category_str.lower() for term in search_terms):
                matching_products += 1
        
        # Calculate confidence based on match percentage
        match_percentage = matching_products / total_products if total_products > 0 else 0
        confidence = min(match_percentage * 2, 1.0)  # Scale to 0-1
        
        analysis[intent] = {
            'rating': rating,
            'matching_products': matching_products,
            'total_products': total_products,
            'confidence': confidence
        }
    
    return analysis

def translate_to_human_response(intent_tags: Dict[str, float], analysis: Dict[str, float], query: str, api_key: str) -> str:
    """
    Use Gemini to translate intent tags and analysis into a human-readable response.
    
    Args:
        intent_tags: Dictionary of intent tags with ratings
        analysis: Analysis results from product matching
        query: Original user query
        api_key: Gemini API key
        
    Returns:
        Human-readable response
    """
    try:
        genai.configure(api_key=api_key)
        
        # Format intent tags and analysis for the prompt
        intent_summary = []
        for intent, rating in intent_tags.items():
            analysis_data = analysis.get(intent, {})
            confidence = analysis_data.get('confidence', 0)
            matching = analysis_data.get('matching_products', 0)
            total = analysis_data.get('total_products', 0)
            
            intent_summary.append(f"- {intent}: {rating:.1f} (confidence: {confidence:.1f}, {matching}/{total} products match)")
        
        intent_text = "\n".join(intent_summary)
        
        prompt = f"""
You are an expert ski equipment advisor. A user asked: "{query}"

Based on analysis of our product database, here are the detected user intents and their ratings:

{intent_text}

INSTRUCTIONS:
1. For questions starting with "Can", "Will", "Does", "Is", "Are", "Would" - BEGIN your response with "Yes" or "No" followed by your explanation
2. Provide a direct, helpful answer to the user's question
3. Use the intent ratings and confidence scores to determine your response
4. High ratings (0.8-1.0) with good confidence (>0.5) = "Yes" followed by positive explanation
5. Medium ratings (0.5-0.7) or low confidence = "Yes, but..." or "Somewhat" with caveats
6. Low ratings (<0.5) or very low confidence = "No" followed by explanation
7. Be specific and practical in your advice
8. Keep the response concise but informative
9. Don't mention technical terms like "intent tags", "confidence scores", or any numerical values
10. NEVER include numerical ratings in your response - use only descriptive terms
11. Speak naturally as if giving advice to a friend

RESPONSE:
"""

        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return "I'm unable to provide a detailed analysis at the moment, but I'd be happy to help with specific product questions."

def get_relevant_products(query: str, df: pd.DataFrame, max_products: int = 20) -> str:
    """
    Get relevant products from the database based on the query.
    
    Args:
        query: The user's query
        df: Product database DataFrame
        max_products: Maximum number of products to include
        
    Returns:
        Formatted string with relevant product information
    """
    if df.empty:
        return ""
    
    query_lower = query.lower()
    relevant_products = []
    
    # Score products based on relevance to query
    for _, product in df.iterrows():
        score = 0
        title = str(product.get('title', '')).lower()
        tags = str(product.get('tags', '')).lower()
        category = str(product.get('category', '')).lower()
        brand = str(product.get('brand', '')).lower()
        
        # Check for query terms in product data
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 2:  # Skip very short words
                if word in title:
                    score += 3
                if word in tags:
                    score += 2
                if word in category:
                    score += 2
                if word in brand:
                    score += 1
        
        # Add general relevance for common skiing terms
        skiing_terms = ['ski', 'skiing', 'offpiste', 'piste', 'park', 'touring', 'freeride', 'allmountain']
        for term in skiing_terms:
            if term in query_lower and (term in tags or term in category):
                score += 1
        
        if score > 0:
            relevant_products.append((score, product))
    
    # Sort by relevance score and take top products
    relevant_products.sort(key=lambda x: x[0], reverse=True)
    top_products = relevant_products[:max_products]
    
    # Format product information
    product_info = []
    for score, product in top_products:
        info = f"""
Product: {product.get('title', 'N/A')}
Brand: {product.get('brand', 'N/A')}
Category: {product.get('category', 'N/A')}
Width: {product.get('waist_width_mm', 'N/A')}mm
Length: {product.get('lengths_cm', 'N/A')}
Twin Tip: {product.get('twintip', 'N/A')}
Price: {product.get('price', 'N/A')} SEK
Gender: {product.get('gender', 'N/A')}
Tags: {product.get('tags', 'N/A')}
"""
        product_info.append(info.strip())
    
    return "\n\n".join(product_info)

def llm_fallback_response(query: str, df: pd.DataFrame, api_key: str) -> str:
    """
    Fallback method using LLM with direct product data when regular approach fails.
    
    Args:
        query: The user's original query
        df: Product database DataFrame
        api_key: Gemini API key
        
    Returns:
        LLM response based on product data
    """
    try:
        genai.configure(api_key=api_key)
        
        # Get relevant products
        relevant_products = get_relevant_products(query, df)
        
        if not relevant_products:
            return "I don't have enough product information to answer your question accurately."
        
        prompt = f"""
You are an expert ski equipment advisor with access to our product database. A customer asked: "{query}"

Here are the most relevant products from our database:

{relevant_products}

INSTRUCTIONS:
1. For questions starting with "Can", "Will", "Does", "Is", "Are", "Would" - BEGIN your response with "Yes" or "No" followed by your explanation
2. Answer the customer's question directly and accurately based on the product data provided
3. Be specific about which products or product characteristics support your answer
4. If the question asks about suitability (e.g., "Will this work for..."), provide a clear yes/no answer with explanation
5. If the question asks about characteristics (e.g., "How stable..."), describe the relevant features
6. Reference specific products by name when relevant
7. Keep the response practical and helpful
8. If the data doesn't contain enough information to answer confidently, say so
9. Speak naturally as if giving advice to a friend

RESPONSE:
"""

        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        logger.info("Used LLM fallback for query response")
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"LLM Fallback Error: {e}")
        return "I'm unable to provide a detailed analysis at the moment, but I'd be happy to help with specific product questions."

def should_use_fallback(intent_tags: Dict[str, float], analysis: Dict[str, float]) -> bool:
    """
    Determine if we should use the LLM fallback instead of the regular approach.
    
    Args:
        intent_tags: Extracted intent tags
        analysis: Analysis results
        
    Returns:
        True if fallback should be used, False otherwise
    """
    # Use fallback if no intent tags were extracted
    if not intent_tags:
        logger.info("No intent tags extracted - using LLM fallback")
        return True
    
    # Use fallback if all confidence scores are very low
    if analysis:
        avg_confidence = sum(data.get('confidence', 0) for data in analysis.values()) / len(analysis)
        if avg_confidence < 0.1:
            logger.info(f"Low average confidence ({avg_confidence:.2f}) - using LLM fallback")
            return True
    
    # Use fallback if no products match any intent
    if analysis:
        total_matches = sum(data.get('matching_products', 0) for data in analysis.values())
        if total_matches == 0:
            logger.info("No matching products found - using LLM fallback")
            return True
    
    return False

def extract_product_from_query(query: str, df: pd.DataFrame) -> Optional[pd.Series]:
    """
    Try to extract a specific product reference from the query.
    Enhanced with fuzzy matching and better partial name handling.
    
    Args:
        query: The user's query
        df: Product database DataFrame
        
    Returns:
        Product Series if found, None otherwise
    """
    query_lower = query.lower()
    
    # Keep track of all matches with scores
    matches = []
    
    # Check for specific product names or brands in the query
    for idx, product in df.iterrows():
        # Clean up title and brand by stripping whitespace
        title = str(product.get('title', '')).strip()
        title_lower = title.lower()
        brand = str(product.get('brand', '')).strip().lower()
        
        # Calculate match score
        score = 0
        
        # Perfect match - exact title in query
        if title_lower and title_lower in query_lower:
            score = 1000  # Highest priority
        else:
            # Split title into meaningful parts
            # Remove common suffixes like "23/24", "24/25", etc.
            title_clean = re.sub(r'\s*\d{2}/\d{2}\s*$', '', title).strip()
            title_parts = title_clean.split()
            
            # Check each part
            parts_found = 0
            important_parts_found = 0
            
            for part in title_parts:
                part_lower = part.lower()
                if len(part_lower) > 1 and part_lower in query_lower:
                    parts_found += 1
                    # Extra weight for numbers and distinctive model names
                    if any(char.isdigit() for char in part) or len(part) > 4:
                        important_parts_found += 1
            
            # Calculate score based on matches
            if len(title_parts) > 0:
                # Base score on percentage of parts found
                match_percentage = parts_found / len(title_parts)
                score = match_percentage * 100
                
                # Bonus for important parts (model numbers, etc.)
                score += important_parts_found * 20
                
                # Special handling for brand + model number patterns
                if brand and brand in query_lower:
                    score += 30
                    # If brand matches and we have at least one other part, it's likely a match
                    if parts_found >= 1:
                        score += 50
                
                # Handle cases where user might not include brand
                # e.g., "Enforcer 89" instead of "Nordica Enforcer 89"
                if parts_found >= 2 or (parts_found >= 1 and important_parts_found >= 1):
                    score += 30
        
        # Only consider matches with reasonable scores
        if score >= 20:
            matches.append((score, idx, product))
    
    # Sort by score and return best match
    if matches:
        matches.sort(key=lambda x: x[0], reverse=True)
        best_score, best_idx, best_product = matches[0]
        
        # Log the match for debugging
        logger.info(f"Product match: '{best_product['title']}' with score {best_score}")
        
        # Return as Series
        return df.iloc[best_idx]
    
    return None

def analyze_single_product(query: str, product: Dict, api_key: str) -> str:
    """
    Analyze a single product based on the query.
    
    Args:
        query: The user's query
        product: Product dictionary
        api_key: Gemini API key
        
    Returns:
        Analysis response for the specific product
    """
    # Use the optimized flex rating system for nuanced responses
    return analyze_single_product_optimized(query, product, api_key)

def analyze_product_with_intents(product: Dict, intent_tags: Dict[str, float]) -> str:
    """
    Analyze a product based on intent tags when LLM is unavailable.
    
    Args:
        product: Product dictionary
        intent_tags: Extracted intent tags
        
    Returns:
        Basic analysis based on tag matching
    """
    tags_str = str(product.get('tags', ''))
    category = str(product.get('category', '')).lower()
    title = product.get('title', 'This product')
    
    responses = []
    
    for intent, rating in intent_tags.items():
        if 'offpiste' in intent:
            if any(term in tags_str for term in ['off-piste', 'powder', 'freeride']):
                responses.append(f"{title} is excellent for off-piste skiing.")
            else:
                responses.append(f"{title} is not specifically designed for off-piste.")
                
        elif 'beginner' in intent:
            if any(term in tags_str for term in ['beginner', 'forgiving', 'easy']):
                responses.append(f"{title} is suitable for beginners.")
            else:
                responses.append(f"{title} may be challenging for beginners.")
                
        elif 'park' in intent:
            if any(term in tags_str for term in ['park', 'freestyle', 'jibbing']):
                responses.append(f"{title} is designed for park skiing.")
            else:
                responses.append(f"{title} is not optimized for park use.")
                
        elif 'lightweight' in intent or 'weight' in intent:
            if any(term in tags_str for term in ['lightweight', 'light', 'carbon']):
                responses.append(f"{title} features lightweight construction.")
            else:
                responses.append(f"{title} has standard weight construction.")
    
    return ' '.join(responses) if responses else f"I need more specific information to analyze {title} for your needs."

def handle_describing_query_with_context(query: str, context_product: Optional[Dict] = None) -> str:
    """
    Handle a descriptive property query with optional context about a specific product.
    
    Args:
        query: The original query that was classified as describing
        context_product: Optional dictionary with product info from chat context
        
    Returns:
        Human-readable response based on intent analysis
    """
    logger.info(f"Processing describing query: {query}")
    
    # Load product database
    df = load_product_database()
    if df.empty:
        return "I don't have access to product information at the moment."
    
    # Get API key
    api_key = get_api_key()
    
    # If we have a context product, use it directly
    if context_product:
        logger.info(f"Using context product: {context_product.get('title', 'Unknown')}")
        return analyze_single_product(query, context_product, api_key)
    
    # Otherwise, check if query mentions a specific product
    specific_product = extract_product_from_query(query, df)
    if specific_product is not None:
        logger.info(f"Found specific product in query: {specific_product.get('title', 'Unknown')}")
        return analyze_single_product(query, specific_product.to_dict(), api_key)
    
    # If no specific product, use the regular approach
    # Extract intent tags from query
    intent_tags = extract_intent_tags(query)
    logger.info(f"Extracted intent tags: {intent_tags}")
    
    # Analyze product matches
    analysis = analyze_product_match(intent_tags, df)
    
    # Check if we should use fallback
    if should_use_fallback(intent_tags, analysis):
        logger.info("Using LLM fallback approach")
        return llm_fallback_response(query, df, api_key)
    
    # Use regular approach
    logger.info("Using regular intent tag approach")
    response = translate_to_human_response(intent_tags, analysis, query, api_key)
    
    return response

def handle_describing_query(query: str) -> str:
    """
    Handle a descriptive property query (backward compatibility wrapper).
    
    Args:
        query: The original query that was classified as describing
        
    Returns:
        Human-readable response based on intent analysis
    """
    # Call the new context-aware function without context
    return handle_describing_query_with_context(query, context_product=None)

def main():
    """Main function for testing."""
    test_queries = [
        "Will this work in offpiste?",
        "Is this good for beginners?",
        "How stable are these skis?",
        "Are these lightweight?",
        "Will this work for park skiing?",
        "Is this suitable for advanced skiers?",
        "Are these good for carving on piste?",
        "How responsive are these skis?",
        "Are these durable?",
        "Will this work for touring?",
        "Are these good for women?",
        "Is this suitable for kids?",
        "Are these wide skis?",
        "How forgiving are these?",
        "Will this work in variable conditions?"
    ]
    
    print("🧪 TESTING DESCRIBING QUERY HANDLER")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: \"{query}\"")
        print("-" * 40)
        
        # Show intent extraction
        intent_tags = extract_intent_tags(query)
        print(f"Intent Tags: {intent_tags}")
        
        # Show full response
        result = handle_describing_query_with_context(query)
        print(f"Response: {result}")
        print()

if __name__ == "__main__":
    main()

##############################
# Deterministic Rule Engine  #
##############################

def evaluate_intents_for_product(intent_tags: Dict[str, float], product: Dict) -> Optional[str]:
    """Evaluate product suitability deterministically based on tags.
    Returns a natural-language answer if confident, otherwise None (meaning fall back to LLM).
    """
    if not intent_tags:
        return None

    tags = str(product.get('tags', '')).lower()
    category = str(product.get('category', '')).lower()
    title = product.get('title', 'This ski')

    responses = []
    confident = True  # If any intent cannot be answered confidently, fall back

    def positive(tlist):
        return any(t in tags or t in category for t in tlist)

    for intent in intent_tags:
        if intent.startswith('function_offpiste'):
            if positive(['off-piste', 'powder', 'freeride', 'backcountry']):
                responses.append("Yes, it will work very well in off-piste conditions.")
            else:
                responses.append("It is not optimised for off-piste skiing.")
        elif intent.startswith('function_piste'):
            if positive(['piste', 'carving', 'all-mountain']):
                responses.append("Yes, it performs well on groomed pistes.")
            else:
                responses.append("Piste performance is not its strongest side.")
        elif intent.startswith('function_park'):
            if positive(['park', 'freestyle', 'jibbing', 'rails']):
                responses.append("Yes, it is designed for park/freestyle riding.")
            else:
                responses.append("It is not really built for park skiing.")
        elif intent.startswith('skill_beginner'):
            if positive(['beginner', 'forgiving', 'easy']):
                responses.append("Yes, it is suitable for beginners.")
            else:
                responses.append("It might be demanding for absolute beginners.")
        elif intent.startswith('performance_stability'):
            if positive(['stable', 'stability', 'control', 'titanal']):
                responses.append("It offers good stability at speed.")
            else:
                responses.append("Stability is average rather than exceptional.")
        elif intent.startswith('performance_weight'):
            if positive(['lightweight', 'light', 'carbon']):
                responses.append("Yes, it is considered lightweight.")
            else:
                responses.append("It has a standard weight construction, not especially light.")
        else:
            confident = False  # Unknown intent -> fallback

    if not confident:
        return None

    # Concatenate responses into single paragraph
    return ' '.join(responses)

def evaluate_product_flex_ratings(product: Dict) -> Dict[str, float]:
    """
    Evaluate a product's characteristics and return flex ratings (0-1) for various aspects.
    This provides numerical ratings that can be interpreted by LLM for nuanced responses.
    
    Args:
        product: Product dictionary with tags, category, etc.
        
    Returns:
        Dictionary mapping characteristics to flex ratings (0-1)
    """
    # Parse the semicolon-separated tags
    tags_raw = str(product.get('tags', '')).lower()
    tags_list = [tag.strip() for tag in tags_raw.split(';') if tag.strip()]
    category = str(product.get('category', '')).lower()
    width = float(product.get('waist_width_mm', 0)) if product.get('waist_width_mm') else 0
    
    ratings = {}
    
    # Helper function to check if any tag from a list is present
    def has_tag(tag_list):
        """Check if any tag from the list is present in the product's tags"""
        return any(tag in tags_list or tag in category for tag in tag_list)
    
    # Function/Usage Ratings - Based on actual tags presence
    
    # Off-piste performance
    if has_tag(['off-piste', 'offpiste', 'powder', 'freeride', 'backcountry', 'float']):
        ratings['offpiste_performance'] = 0.8
        if has_tag(['powder']) and has_tag(['freeride']):
            ratings['offpiste_performance'] = 0.9
    elif has_tag(['all-mountain', 'allmountain']):
        # All-mountain skis are decent off-piste
        ratings['offpiste_performance'] = 0.6
    else:
        ratings['offpiste_performance'] = 0.3
    
    # Piste performance
    if has_tag(['piste', 'carving', 'groomed', 'race', 'edge-hold', 'edge-grip']):
        ratings['piste_performance'] = 0.9
    elif has_tag(['all-mountain', 'allmountain', 'versatile']):
        # All-mountain skis are good on piste
        ratings['piste_performance'] = 0.7
    elif has_tag(['park', 'freestyle']):
        ratings['piste_performance'] = 0.5
    else:
        ratings['piste_performance'] = 0.4
    
    # Park performance
    if has_tag(['park', 'freestyle', 'jibbing', 'rails', 'jumps', 'playful', 'twin-tip']):
        ratings['park_performance'] = 0.9
        if has_tag(['pro-model', 'park-slayer']):
            ratings['park_performance'] = 1.0
    elif has_tag(['all-mountain', 'versatile']):
        ratings['park_performance'] = 0.5
    else:
        ratings['park_performance'] = 0.2
    
    # Touring capability
    if has_tag(['touring', 'freetouring', 'backcountry', 'uphill', 'lightweight', 'carbon']):
        ratings['touring_capability'] = 0.8
        if 'topptursskidor' in category:
            ratings['touring_capability'] = 0.9
    else:
        ratings['touring_capability'] = 0.2
    
    # Skill Level Suitability
    if has_tag(['beginner', 'forgiving', 'easy', 'soft-flex', 'easy-turn']):
        ratings['beginner_friendly'] = 0.9
    elif has_tag(['intermediate']):
        ratings['beginner_friendly'] = 0.5
    elif has_tag(['expert', 'advanced', 'aggressive', 'demanding']):
        ratings['beginner_friendly'] = 0.2
    else:
        ratings['beginner_friendly'] = 0.4
    
    # Expert performance
    if has_tag(['expert', 'advanced', 'aggressive', 'responsive', 'precise', 'pro-model']):
        ratings['expert_performance'] = 0.9
    elif has_tag(['intermediate', 'advanced']):
        ratings['expert_performance'] = 0.7
    else:
        ratings['expert_performance'] = 0.4
    
    # Physical Characteristics
    if width > 0:
        # Width rating: <85mm=0.2, 85-95mm=0.4, 95-105mm=0.6, 105-115mm=0.8, >115mm=1.0
        if width < 85:
            ratings['width_rating'] = 0.2
        elif width < 95:
            ratings['width_rating'] = 0.4
        elif width < 105:
            ratings['width_rating'] = 0.6
        elif width < 115:
            ratings['width_rating'] = 0.8
        else:
            ratings['width_rating'] = 1.0
    
    # Performance Characteristics
    if has_tag(['stable', 'stability', 'titanal', 'metal', 'damp', 'control']):
        ratings['stability'] = 0.8
    elif has_tag(['playful', 'agile', 'nimble']):
        ratings['stability'] = 0.5
    else:
        ratings['stability'] = 0.6
    
    # Agility
    if has_tag(['agile', 'nimble', 'responsive', 'quick', 'playful', 'maneuverable']):
        ratings['agility'] = 0.8
    elif has_tag(['stable', 'damp', 'heavy']):
        ratings['agility'] = 0.4
    else:
        ratings['agility'] = 0.6
    
    # Speed performance
    if has_tag(['fast', 'speed', 'race', 'aggressive', 'titanal']):
        ratings['speed_performance'] = 0.9
    elif has_tag(['park', 'freestyle']):
        ratings['speed_performance'] = 0.5
    else:
        ratings['speed_performance'] = 0.6
    
    # Conditions - Hard snow
    if has_tag(['ice', 'icy', 'hardpack', 'edge-hold', 'carving', 'race', 'metal', 'edge-grip']):
        ratings['hard_snow_performance'] = 0.8
    elif has_tag(['all-mountain', 'piste']):
        ratings['hard_snow_performance'] = 0.6
    else:
        ratings['hard_snow_performance'] = 0.4
    
    # Soft snow/powder
    if has_tag(['powder', 'float', 'soft-snow', 'freeride']):
        ratings['soft_snow_performance'] = 0.9
    elif has_tag(['all-mountain', 'versatile']) or width >= 100:
        ratings['soft_snow_performance'] = 0.7
    else:
        ratings['soft_snow_performance'] = 0.4
    
    # Special adjustments for all-mountain/versatile skis
    if has_tag(['all-mountain', 'allmountain', 'versatile']):
        # All-mountain skis should have balanced ratings
        for key in ['offpiste_performance', 'piste_performance']:
            if key in ratings and ratings[key] < 0.6:
                ratings[key] = 0.6
    
    return ratings

def interpret_flex_ratings_fast(query: str, product: Dict, ratings: Dict[str, float], api_key: str) -> str:
    """
    Use LLM to interpret flex ratings into natural language response.
    Enhanced to include actual technical specifications from the database.
    
    Args:
        query: Original user query
        product: Product information
        ratings: Flex ratings dictionary
        api_key: Gemini API key
        
    Returns:
        Natural language interpretation with technical specs
    """
    try:
        genai.configure(api_key=api_key)
        
        # Get the actual tags for context
        tags = str(product.get('tags', '')).lower().split(';')
        category = str(product.get('category', '')).lower()
        
        # EXTRACT TECHNICAL SPECIFICATIONS from actual data
        tech_specs = []
        
        # Waist width
        width = product.get('waist_width_mm', None)
        if width and pd.notna(width):
            tech_specs.append(f"Waist width: {width}mm")
        
        # Length options
        lengths = product.get('lengths_cm', None)
        if lengths and pd.notna(lengths):
            if isinstance(lengths, str):
                length_list = lengths.replace(';', ', ')
                tech_specs.append(f"Available lengths: {length_list}cm")
            else:
                tech_specs.append(f"Length: {lengths}cm")
        
        # Twin tip status - CRITICAL FIX
        twin_tip = product.get('twin_tip', None)
        if twin_tip is not None:
            tech_specs.append(f"Twin tip: {'Yes' if twin_tip else 'No'}")
        
        # Price information
        price = product.get('price', None)
        reapris = product.get('reapris', None)
        if price and pd.notna(price):
            price_text = f"Price: {price} SEK"
            if reapris and pd.notna(reapris):
                price_text += f" (Sale: {reapris} SEK)"
            tech_specs.append(price_text)
        
        # Extract weight from tags (look for pattern like "1410g")
        tags_str = str(product.get('tags', ''))
        import re
        weight_match = re.search(r'(\d+(?:\.\d+)?)g', tags_str)
        if weight_match:
            weight = weight_match.group(0)
            tech_specs.append(f"Weight: {weight}")
        
        # Extract turn radius from tags
        radius_patterns = [r'(\d+(?:\.\d+)?)m-radius', r'(\d+(?:\.\d+)?)m\s*radius', r'radius[:\-\s]*(\d+(?:\.\d+)?)m?']
        for pattern in radius_patterns:
            radius_match = re.search(pattern, tags_str, re.IGNORECASE)
            if radius_match:
                radius = radius_match.group(1)
                tech_specs.append(f"Turn radius: {radius}m")
                break
        
        # Stock/availability
        stock = product.get('storlek_i_lager', None)
        if stock and pd.notna(stock) and str(stock).strip() != '':
            tech_specs.append(f"In stock: {stock}cm")
        
        # Gender
        gender = product.get('gender', None) 
        if gender and pd.notna(gender):
            tech_specs.append(f"Gender: {gender}")
        
        # Check for specific attribute queries
        query_lower = query.lower()
        
        # CRITICAL: Direct answers for specific attributes
        if 'twintip' in query_lower or 'twin tip' in query_lower or 'twin-tip' in query_lower:
            # Direct answer for twin-tip question
            if twin_tip is not None:
                direct_answer = "Yes" if twin_tip else "No"
                return f"{direct_answer}, the {product.get('title', 'product')} {'is' if twin_tip else 'is not'} a twin-tip ski."
            else:
                return f"Twin-tip information is not available for the {product.get('title', 'product')}."
        
        if 'price' in query_lower or 'cost' in query_lower or 'how much' in query_lower:
            # Direct answer for price question
            if price and pd.notna(price):
                response = f"The {product.get('title', 'product')} costs {price} SEK"
                if reapris and pd.notna(reapris):
                    response += f", currently on sale for {reapris} SEK."
                else:
                    response += "."
                return response
            else:
                return f"Price information is not available for the {product.get('title', 'product')}."
        
        # Extract only relevant ratings based on query
        relevant_ratings = {}
        
        # Map query terms to relevant ratings - include more context
        if any(term in query_lower for term in ['offpiste', 'off-piste', 'powder', 'backcountry', 'deep']):
            relevant_ratings['Off-piste performance'] = ratings.get('offpiste_performance', 0.5)
            relevant_ratings['Soft snow performance'] = ratings.get('soft_snow_performance', 0.5)
        
        if any(term in query_lower for term in ['piste', 'groomed', 'carving', 'hardpack', 'edge']):
            relevant_ratings['Piste performance'] = ratings.get('piste_performance', 0.5)
            relevant_ratings['Hard snow performance'] = ratings.get('hard_snow_performance', 0.5)
            relevant_ratings['Stability'] = ratings.get('stability', 0.5)
        
        if any(term in query_lower for term in ['park', 'freestyle', 'jumps', 'rails']):
            relevant_ratings['Park performance'] = ratings.get('park_performance', 0.5)
            relevant_ratings['Agility'] = ratings.get('agility', 0.5)
        
        if any(term in query_lower for term in ['beginner', 'learning', 'easy']):
            relevant_ratings['Beginner friendliness'] = ratings.get('beginner_friendly', 0.5)
            relevant_ratings['Stability'] = ratings.get('stability', 0.5)
        
        if any(term in query_lower for term in ['touring', 'uphill', 'skinning']):
            relevant_ratings['Touring capability'] = ratings.get('touring_capability', 0.5)
        
        if any(term in query_lower for term in ['stable', 'stability', 'charging']):
            relevant_ratings['Stability'] = ratings.get('stability', 0.5)
            relevant_ratings['Speed performance'] = ratings.get('speed_performance', 0.5)
        
        if any(term in query_lower for term in ['mogul', 'bumps', 'technical', 'tree']):
            relevant_ratings['Agility'] = ratings.get('agility', 0.5)
            relevant_ratings['Responsiveness'] = ratings.get('agility', 0.5)
        
        if any(term in query_lower for term in ['spring', 'slush', 'variable', 'unpredictable']):
            relevant_ratings['Versatility'] = (ratings.get('offpiste_performance', 0.5) + 
                                             ratings.get('piste_performance', 0.5)) / 2
            relevant_ratings['All-mountain capability'] = 0.8 if 'all-mountain' in tags else 0.5
        
        # If asking for specific specs, focus on technical data only
        if any(term in query_lower for term in ['width', 'waist', 'weight', 'radius', 'length', 'specs', 'specification']):
            relevant_ratings = {}  # Focus on technical specs only
        
        # If no specific ratings identified and no spec question, use general performance metrics
        if not relevant_ratings and not any(term in query_lower for term in ['width', 'waist', 'weight', 'radius', 'length', 'specs']):
            relevant_ratings = {
                'Off-piste performance': ratings.get('offpiste_performance', 0.5),
                'Piste performance': ratings.get('piste_performance', 0.5),
                'Overall versatility': (ratings.get('offpiste_performance', 0.5) + 
                                      ratings.get('piste_performance', 0.5)) / 2
            }
        
        # Format ratings for prompt (if any)
        rating_text = []
        for aspect, rating in relevant_ratings.items():
            if rating >= 0.8:
                level = "Excellent"
            elif rating >= 0.6:
                level = "Good"
            elif rating >= 0.4:
                level = "Moderate"
            elif rating >= 0.2:
                level = "Limited"
            else:
                level = "Poor"
            rating_text.append(f"{aspect}: {level}")
        
        # Determine ski type from tags/category
        ski_type = "ski"
        if 'all-mountain' in tags or 'allmountain' in category:
            ski_type = "all-mountain ski"
        elif 'freeride' in tags or 'freerideskidor' in category:
            ski_type = "freeride ski"
        elif 'park' in tags or 'parkskidor' in category:
            ski_type = "park ski"
        elif 'touring' in tags or 'topptursskidor' in category:
            ski_type = "touring ski"
        
        # BUILD ENHANCED PROMPT with technical specifications
        prompt_parts = [f'Question: "{query}"']
        prompt_parts.append(f'Product: {product.get("title", "This ski")} (a {ski_type})')
        
        # Add technical specifications if available
        if tech_specs:
            prompt_parts.append(f'\nTechnical Specifications:\n' + '\n'.join(tech_specs))
        
        # Add performance ratings if relevant
        if rating_text:
            prompt_parts.append(f'\nPerformance ratings:\n' + '\n'.join(rating_text))
        
        prompt_parts.append(f"""
INSTRUCTIONS: 
1. For questions asking specific specs (width, weight, radius, length) - provide the EXACT numbers from the specifications
2. For yes/no questions - START with "Yes", "No", or "Yes, but..." based on the data
3. Be specific and cite actual measurements when available
4. If specs are requested but not available, clearly state what data is missing
5. Use natural language, avoid overly technical jargon
6. Keep response focused and informative

Example good responses for spec questions:
- "The Fischer Transalp 98 CTI 23/24 has a waist width of 98mm and weighs 1410g, making it efficient for uphill tours due to its lightweight construction."
- "According to the specifications, the Salomon Départ 1.0 has a 15m turn radius and comes in 170cm and 180cm lengths. Weight information is not available in the current data."
- "The Line Pandora 99 has a 99mm waist width while the Line Chronic 94 has a 94mm waist. Both are lightweight designs, but specific weight comparisons require additional data."

Response:""")

        prompt = '\n'.join(prompt_parts)
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt, 
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Very low temperature for factual accuracy
                max_output_tokens=200  # More tokens for detailed spec responses
            ))
        
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Flex rating interpretation error: {e}")
        # Enhanced fallback that includes specs
        return create_simple_interpretation_with_specs(query, relevant_ratings, product)

def create_simple_interpretation(query: str, ratings: Dict[str, float], product: Dict = None) -> str:
    """
    Create a better rule-based interpretation when LLM fails.
    
    Args:
        query: Original query
        ratings: Relevant ratings dictionary
        product: Product dictionary (optional, for better context)
        
    Returns:
        Natural language response based on ratings and product info
    """
    if not ratings:
        return "I need more information to analyze this product's performance."
    
    # Get product context
    product_name = product.get('title', 'This ski') if product else 'This ski'
    tags = str(product.get('tags', '')).lower().split(';') if product else []
    category = str(product.get('category', '')).lower() if product else ''
    
    # Determine ski type
    ski_type = "ski"
    if 'all-mountain' in tags or 'allmountain' in category:
        ski_type = "all-mountain ski"
    elif 'freeride' in tags or 'freerideskidor' in category:
        ski_type = "freeride ski"
    elif 'park' in tags or 'parkskidor' in category:
        ski_type = "park ski"
    elif 'touring' in tags or 'topptursskidor' in category:
        ski_type = "touring ski"
    
    # Find the highest and lowest ratings
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    best = sorted_ratings[0] if sorted_ratings else None
    worst = sorted_ratings[-1] if len(sorted_ratings) > 1 else None
    
    # Check if query is yes/no
    is_yes_no = any(query.lower().startswith(word) for word in ['will', 'can', 'does', 'is', 'are'])
    
    # Build response based on ratings
    if best and best[1] >= 0.7:
        # Good performance
        aspect = best[0].lower().replace('_', ' ')
        if is_yes_no:
            response = f"Yes, {product_name} "
        else:
            response = f"{product_name} "
            
        if 'powder' in query.lower() or 'offpiste' in query.lower():
            if best[0] == 'Off-piste performance' or best[0] == 'Soft snow performance':
                response += f"performs well in those conditions. "
            else:
                response += f"has {aspect} but may not be ideal for deep powder. "
                
        elif 'carving' in query.lower() or 'groomed' in query.lower() or 'hardpack' in query.lower():
            if best[0] == 'Piste performance' or best[0] == 'Hard snow performance':
                response += f"excels in those conditions. "
            else:
                response += f"has {aspect} but isn't optimized for hardpack. "
                
        elif 'touring' in query.lower() or 'uphill' in query.lower():
            if best[0] == 'Touring capability':
                response += f"is well-suited for touring. "
            else:
                response += f"has {aspect} but isn't designed for touring. "
                
        else:
            response += f"offers good {aspect}. "
            
        # Add ski type context
        if ski_type != "ski":
            response += f"As {ski_type.replace('ski', 'a ' + ski_type)}, it's designed for "
            if 'all-mountain' in ski_type:
                response += "versatile performance across conditions."
            elif 'park' in ski_type:
                response += "freestyle and park riding."
            elif 'freeride' in ski_type:
                response += "off-piste and powder skiing."
            elif 'touring' in ski_type:
                response += "backcountry and uphill travel."
                
    elif best and best[1] >= 0.4:
        # Moderate performance
        aspect = best[0].lower().replace('_', ' ')
        if is_yes_no:
            response = f"Yes, but with limitations. {product_name} has moderate {aspect}. "
        else:
            response = f"{product_name} offers moderate {aspect}. "
            
        # Suggest what it's better for based on tags
        if 'park' in tags:
            response += "It's better suited for park and freestyle skiing."
        elif 'powder' in tags or 'freeride' in tags:
            response += "It's better suited for off-piste and powder conditions."
        elif 'piste' in tags or 'carving' in tags:
            response += "It's better suited for groomed runs."
            
    else:
        # Poor performance for the asked feature
        if is_yes_no:
            response = f"No, {product_name} isn't well-suited for that. "
        else:
            response = f"{product_name} has limited capability in those conditions. "
            
        # Suggest what it IS good for based on tags
        if 'park' in tags:
            response += "This ski is designed for park and freestyle skiing instead."
        elif 'powder' in tags or 'freeride' in tags:
            response += "This ski is designed for off-piste and powder skiing instead."
        elif 'piste' in tags or 'carving' in tags:
            response += "This ski is designed for groomed runs instead."
        elif 'all-mountain' in tags:
            response += "As an all-mountain ski, it performs better in mixed conditions."
    
    return response.strip()

def create_simple_interpretation_with_specs(query: str, ratings: Dict[str, float], product: Dict = None) -> str:
    """
    Enhanced fallback interpretation that includes technical specifications.
    
    Args:
        query: Original query
        ratings: Relevant ratings dictionary
        product: Product dictionary (optional, for better context)
        
    Returns:
        Natural language response with technical specs
    """
    if not product:
        return "I need more information to analyze this product's performance."
    
    # Get product context
    product_name = product.get('title', 'This ski')
    tags = str(product.get('tags', '')).lower().split(';')
    
    # Extract technical specs for fallback
    specs = []
    width = product.get('waist_width_mm', None)
    if width and pd.notna(width):
        specs.append(f"waist width of {width}mm")
    
    lengths = product.get('lengths_cm', None)
    if lengths and pd.notna(lengths):
        if isinstance(lengths, str):
            length_list = lengths.replace(';', ', ')
            specs.append(f"available in {length_list}cm lengths")
    
    # Extract weight from tags
    tags_str = str(product.get('tags', ''))
    weight_match = re.search(r'(\d+(?:\.\d+)?)g', tags_str)
    if weight_match:
        specs.append(f"weighs {weight_match.group(0)}")
    
    # Extract turn radius from tags
    radius_patterns = [r'(\d+(?:\.\d+)?)m-radius', r'(\d+(?:\.\d+)?)m\s*radius']
    for pattern in radius_patterns:
        radius_match = re.search(pattern, tags_str, re.IGNORECASE)
        if radius_match:
            specs.append(f"{radius_match.group(1)}m turn radius")
            break
    
    # Build response with specs
    if specs:
        specs_text = ", ".join(specs)
        response = f"The {product_name} has a {specs_text}."
        
        # Add context based on query
        if any(term in query.lower() for term in ['touring', 'uphill']):
            if 'lightweight' in tags or any('g' in spec for spec in specs):
                response += " This makes it suitable for touring applications."
        
        return response
    
    # Fallback to original function if no specs available
    return create_simple_interpretation(query, ratings, product)

def analyze_single_product_optimized(query: str, product: Dict, api_key: str) -> str:
    """
    Optimized version of analyze_single_product using flex ratings for nuanced responses.
    Target: <1 second response time with 100% accuracy.
    
    Args:
        query: The user's query
        product: Product dictionary
        api_key: Gemini API key
        
    Returns:
        Analysis response for the specific product
    """
    try:
        # Step 1: Extract intent tags (fast, <1ms)
        intent_tags = extract_intent_tags(query)
        
        # Step 2: Get flex ratings for the product (fast, <5ms)
        flex_ratings = evaluate_product_flex_ratings(product)
        
        # Step 3: Use LLM to interpret ratings into natural language (target: <900ms)
        response = interpret_flex_ratings_fast(query, product, flex_ratings, api_key)
        
        logger.info("Analyzed product with flex rating system")
        return response
        
    except Exception as e:
        logger.error(f"Optimized analysis error: {e}")
        # Fallback to deterministic rule engine
        deterministic = evaluate_intents_for_product(intent_tags, product)
        if deterministic:
            return deterministic
        # If deterministic fails, use improved fallback with product context
        return create_simple_interpretation_with_specs(query, flex_ratings, product) 