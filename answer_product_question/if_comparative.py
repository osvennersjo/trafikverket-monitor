#!/usr/bin/env python3
"""
If Comparative - Handler for Comparative Property Queries

This file handles queries classified as "query=property;compare"
Comparative queries ask to compare two or more different products in any regard.

Examples:
- "Which is better, these skis or those skis?"
- "Compare the waterproofing of these two jackets"
- "Are these boots warmer than those boots?"
- "Which ski is best for off-piste?"
"""

import os
import sys
import logging
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
import google.generativeai as genai

# Import functions from if_describing for flex ratings
try:
    # Try relative import first (when used as module)
    from .if_describing import (
        get_api_key,
        load_product_database,
        extract_intent_tags,
        evaluate_product_flex_ratings,
        extract_product_from_query
    )
except ImportError:
    # Fallback to absolute import (when run directly)
    from if_describing import (
        get_api_key,
        load_product_database,
        extract_intent_tags,
        evaluate_product_flex_ratings,
        extract_product_from_query
    )

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_comparison_intent_tags(query: str) -> Dict[str, float]:
    """
    Extract intent tags from comparative query.
    Uses the same function as if_describing for consistency.
    
    Args:
        query: The comparative query
        
    Returns:
        Dictionary of intent tags with their importance ratings
    """
    return extract_intent_tags(query)

def map_intent_tags_to_rating_aspects(intent_tags: Dict[str, float]) -> List[str]:
    """
    Map intent tags to specific flex rating aspects.
    
    Args:
        intent_tags: Dictionary of intent tags
        
    Returns:
        List of rating aspect keys to compare
    """
    aspects = []
    
    for intent in intent_tags:
        if 'offpiste' in intent:
            aspects.extend(['offpiste_performance', 'soft_snow_performance'])
        elif 'piste' in intent:
            aspects.extend(['piste_performance', 'hard_snow_performance'])
        elif 'park' in intent:
            aspects.extend(['park_performance', 'agility'])
        elif 'touring' in intent:
            aspects.extend(['touring_capability', 'performance_weight'])
        elif 'allmountain' in intent:
            aspects.extend(['offpiste_performance', 'piste_performance'])
        elif 'freeride' in intent:
            aspects.extend(['offpiste_performance', 'soft_snow_performance'])
        elif 'beginner' in intent:
            aspects.extend(['beginner_friendly', 'stability'])
        elif 'intermediate' in intent:
            aspects.append('beginner_friendly')
        elif 'advanced' in intent or 'expert' in intent:
            aspects.extend(['expert_performance', 'speed_performance'])
        elif 'stability' in intent:
            aspects.append('stability')
        elif 'weight' in intent:
            aspects.append('performance_weight')
        elif 'speed' in intent:
            aspects.append('speed_performance')
        elif 'responsiveness' in intent:
            aspects.append('agility')
        elif 'forgiving' in intent:
            aspects.append('beginner_friendly')
        elif 'durability' in intent:
            aspects.append('stability')  # Use stability as proxy for build quality
        elif 'control' in intent:
            aspects.extend(['stability', 'hard_snow_performance'])
        elif 'width' in intent:
            aspects.append('width_rating')
        elif 'narrow' in intent:
            aspects.append('width_rating')
        elif 'ice' in intent:
            aspects.append('hard_snow_performance')
        elif 'moguls' in intent:
            aspects.append('agility')
        elif 'women' in intent:
            aspects.append('beginner_friendly')  # Often correlates with lighter/easier
        elif 'junior' in intent:
            aspects.append('beginner_friendly')
    
    # Remove duplicates while preserving order
    seen = set()
    unique_aspects = []
    for aspect in aspects:
        if aspect not in seen:
            seen.add(aspect)
            unique_aspects.append(aspect)
    
    # If no specific aspects identified, compare main performance metrics
    if not unique_aspects:
        unique_aspects = ['offpiste_performance', 'piste_performance']
    
    return unique_aspects

def compare_products_by_aspects(products_data: List[Dict], aspects: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Compare products across specified aspects.
    
    Args:
        products_data: List of products with their flex ratings
        aspects: List of aspects to compare
        
    Returns:
        Dictionary mapping aspects to product ratings
    """
    comparison = {}
    
    for aspect in aspects:
        comparison[aspect] = {}
        for product_data in products_data:
            title = product_data['info'].get('title', 'Unknown')
            rating = product_data['ratings'].get(aspect, 0.5)
            comparison[aspect][title] = rating
    
    return comparison

def interpret_comparison_fast(query: str, comparison_data: Dict[str, Dict[str, float]], 
                            intent_tags: Dict[str, float], api_key: str) -> str:
    """
    Use LLM to interpret comparison results into natural language.
    Optimized for speed with minimal prompt.
    
    Args:
        query: Original query
        comparison_data: Comparison data by aspects
        intent_tags: Original intent tags from query
        api_key: Gemini API key
        
    Returns:
        Natural language comparison
    """
    try:
        genai.configure(api_key=api_key)
        
        # Format comparison for prompt
        comparison_text = []
        
        # Get all products
        all_products = set()
        for aspect_data in comparison_data.values():
            all_products.update(aspect_data.keys())
        
        # Create comparison table
        for product in sorted(all_products):
            comparison_text.append(f"\n{product}:")
            for aspect, ratings in comparison_data.items():
                if product in ratings:
                    rating = ratings[product]
                    # Convert to descriptive level
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
                    
                    aspect_name = aspect.replace('_', ' ').replace('performance', '').strip()
                    comparison_text.append(f"  - {aspect_name}: {level} ({rating:.1f})")
        
        comparison_str = "\n".join(comparison_text)
        
        # Minimal prompt for speed
        prompt = f"""Query: "{query}"

Product ratings:
{comparison_str}

INSTRUCTIONS:
For questions asking "Which" or "Should I choose", directly state the better product first.
Answer which product is best for what the user asked. Use ONLY the descriptive levels (Excellent, Good, etc.) - NEVER mention the numerical ratings. Keep it under 2 sentences."""

        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt, 
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=100
            ))
        
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"LLM comparison error: {e}")
        # Fallback to rule-based
        return create_deterministic_comparison(comparison_data, intent_tags)

def create_deterministic_comparison(comparison_data: Dict[str, Dict[str, float]], 
                                  intent_tags: Dict[str, float]) -> str:
    """
    Create a deterministic comparison when LLM fails.
    
    Args:
        comparison_data: Comparison data by aspects
        intent_tags: Original intent tags
        
    Returns:
        Simple comparison text
    """
    if not comparison_data:
        return "I couldn't compare these products."
    
    # Get the primary aspect (first one)
    primary_aspect = list(comparison_data.keys())[0]
    ratings = comparison_data[primary_aspect]
    
    if not ratings:
        return "No products to compare."
    
    # Find best product
    best_product = max(ratings.items(), key=lambda x: x[1])
    best_rating_value = best_product[1]
    
    # Convert rating to descriptive level
    if best_rating_value >= 0.8:
        level = "excellent"
    elif best_rating_value >= 0.6:
        level = "good"
    elif best_rating_value >= 0.4:
        level = "moderate"
    else:
        level = "limited"
    
    # Check if there's a clear winner
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_ratings) > 1:
        diff = sorted_ratings[0][1] - sorted_ratings[1][1]
        if diff > 0.2:
            aspect_name = primary_aspect.replace('_', ' ').replace('performance', '').strip()
            return f"{best_product[0]} is better for {aspect_name} with {level} performance."
        else:
            return f"Both products perform similarly for {primary_aspect.replace('_', ' ')}."
    
    aspect_name = primary_aspect.replace('_', ' ').replace('performance', '').strip()
    return f"{best_product[0]} has {level} {aspect_name}."

def extract_products_for_comparison_fallback(query: str, df: pd.DataFrame) -> List[pd.Series]:
    """
    Enhanced fallback method to extract products from query when not in context.
    Focuses on exact product matches mentioned in the query.
    
    Args:
        query: The comparative query
        df: Product database DataFrame
        
    Returns:
        List of product Series
    """
    query_lower = query.lower()
    found_products = []
    
    # Enhanced matching for specific product names mentioned in query
    for _, product in df.iterrows():
        title = str(product.get('title', '')).lower()
        brand = str(product.get('brand', '')).lower()
        
        # Method 1: Direct substring matching (most reliable)
        if title and title in query_lower:
            found_products.append(product)
            continue
            
        # Method 2: Specific product name matching
        # Extract potential product names from query (words after brand names)
        title_words = title.split()
        brand_in_query = brand and brand in query_lower
        
        if brand_in_query and len(title_words) >= 2:
            # Check if the main product identifiers are in the query
            product_identifiers = []
            for word in title_words[1:]:  # Skip brand name
                if len(word) >= 2:
                    product_identifiers.append(word)
            
            # Must find at least 2 key identifiers or a number-containing identifier
            matches = 0
            has_number_match = False
            
            for identifier in product_identifiers:
                if identifier in query_lower:
                    matches += 1
                    if any(char.isdigit() for char in identifier):
                        has_number_match = True
            
            # Only add if we have strong evidence this specific product is mentioned
            if (matches >= 2) or (has_number_match and matches >= 1):
                found_products.append(product)
    
    # Remove duplicates while preserving order
    seen_titles = set()
    unique_products = []
    for product in found_products:
        title = product.get('title', '')
        if title not in seen_titles and title:  # Ensure title is not empty
            seen_titles.add(title)
            unique_products.append(product)
    
    # If we found too many products, try to narrow down to most relevant ones
    if len(unique_products) > 5:
        # Score products by how well they match the query
        scored_products = []
        for product in unique_products:
            title = product.get('title', '').lower()
            score = 0
            
            # Count exact word matches
            title_words = title.split()
            for word in title_words:
                if word in query_lower:
                    score += 1
                    # Bonus for numbers (model identifiers)
                    if any(char.isdigit() for char in word):
                        score += 2
            
            scored_products.append((score, product))
        
        # Sort by score and take top products
        scored_products.sort(key=lambda x: x[0], reverse=True)
        unique_products = [product for score, product in scored_products[:5]]
    
    return unique_products

def compare_products_by_price(products_data: List[Dict]) -> str:
    """
    Compare products by price, handling both regular and sale prices.
    
    Args:
        products_data: List of products with their info
        
    Returns:
        Natural language price comparison
    """
    price_info = []
    
    for product_data in products_data:
        product = product_data['info']
        title = product.get('title', 'Unknown')
        price = product.get('price', None)
        reapris = product.get('reapris', None)
        
        if price and pd.notna(price):
            current_price = reapris if (reapris and pd.notna(reapris)) else price
            price_info.append({
                'title': title,
                'original_price': float(price),
                'sale_price': float(reapris) if (reapris and pd.notna(reapris)) else None,
                'current_price': float(current_price)
            })
    
    if not price_info:
        return "Price information is not available for these products."
    
    # Sort by current price
    price_info.sort(key=lambda x: x['current_price'])
    
    # Build response
    response_parts = []
    
    # Identify cheapest
    cheapest = price_info[0]
    response_parts.append(f"The cheapest option is {cheapest['title']} at {cheapest['current_price']} SEK")
    if cheapest['sale_price']:
        response_parts[0] += f" (on sale from {cheapest['original_price']} SEK)"
    
    # List all prices
    response_parts.append("\n\nFull price comparison:")
    for item in price_info:
        price_text = f"- {item['title']}: {item['current_price']} SEK"
        if item['sale_price']:
            price_text += f" (sale price, originally {item['original_price']} SEK)"
        response_parts.append(price_text)
    
    return "\n".join(response_parts)

def compare_products_by_length_constraint(products_data: List[Dict], height_cm: int, max_over_height: int = 5) -> str:
    """
    Compare products based on length constraints for a given height.
    
    Args:
        products_data: List of products with their info
        height_cm: User's height in cm
        max_over_height: Maximum acceptable length over height
        
    Returns:
        Natural language comparison with length recommendations
    """
    max_length = height_cm + max_over_height
    suitable_products = []
    unsuitable_products = []
    
    for product_data in products_data:
        product = product_data['info']
        title = product.get('title', 'Unknown')
        lengths_str = product.get('lengths_cm', '')
        min_length = product.get('min_length_cm', None)
        
        if min_length and pd.notna(min_length):
            min_length = int(min_length)
            if min_length <= max_length:
                suitable_products.append({
                    'title': title,
                    'min_length': min_length,
                    'lengths': lengths_str,
                    'over_height': min_length - height_cm
                })
            else:
                unsuitable_products.append({
                    'title': title,
                    'min_length': min_length,
                    'lengths': lengths_str,
                    'over_height': min_length - height_cm
                })
    
    # Build response
    response_parts = []
    
    if suitable_products:
        response_parts.append(f"For your height of {height_cm}cm (max {max_length}cm), suitable options are:")
        for product in suitable_products:
            response_parts.append(f"✅ {product['title']}: Available from {product['min_length']}cm (lengths: {product['lengths']})")
    
    if unsuitable_products:
        if suitable_products:
            response_parts.append("\nNot suitable due to length:")
        else:
            response_parts.append(f"None of these skis fit your requirement of max {max_length}cm:")
        for product in unsuitable_products:
            response_parts.append(f"❌ {product['title']}: Minimum {product['min_length']}cm ({product['over_height'] - max_over_height}cm too long)")
    
    if suitable_products:
        # Recommend the best option
        best = min(suitable_products, key=lambda x: x['over_height'])
        response_parts.append(f"\nBest fit: {best['title']} at {best['min_length']}cm")
    
    return "\n".join(response_parts)

def extract_height_from_query(query: str) -> Optional[int]:
    """
    Extract height information from query.
    
    Args:
        query: User's query
        
    Returns:
        Height in cm if found, None otherwise
    """
    import re
    # Look for patterns like "160cm", "I am 160cm", "I'm 165 cm tall"
    height_patterns = [
        r'(\d{3})\s*cm',
        r'(\d{3})\s*centimeters?',
        r"i'?m?\s+(\d{3})",
        r'height.*?(\d{3})',
        r'(\d{3}).*?tall'
    ]
    
    query_lower = query.lower()
    for pattern in height_patterns:
        match = re.search(pattern, query_lower)
        if match:
            height = int(match.group(1))
            # Sanity check - reasonable human height
            if 140 <= height <= 220:
                return height
    
    return None

def extract_products_for_comparison_enhanced(query: str, df: pd.DataFrame) -> List[pd.Series]:
    """
    Enhanced product extraction using the improved logic from if_describing.
    
    Args:
        query: The comparative query
        df: Product database DataFrame
        
    Returns:
        List of product Series
    """
    products = []
    
    # Use the improved extraction logic for each potential product mention
    # Split query by common separators
    import re
    potential_products = re.split(r'\s+(?:or|and|vs|versus|,)\s+', query, flags=re.IGNORECASE)
    
    for potential in potential_products:
        product = extract_product_from_query(potential.strip(), df)
        if product is not None and not any(product.equals(p) for p in products):
            products.append(product)
    
    # If that didn't work, try the original fallback method
    if len(products) < 2:
        products.extend(extract_products_for_comparison_fallback(query, df))
    
    # Remove duplicates
    unique_products = []
    seen_titles = set()
    for product in products:
        title = product.get('title', '')
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_products.append(product)
    
    return unique_products

def handle_comparative_query_with_context(query: str, context_products: Optional[List[Dict]] = None) -> str:
    """
    Handle a comparative property query with optional context products.
    Enhanced to handle price and length comparisons.
    
    Args:
        query: The original query that was classified as comparative
        context_products: Optional list of products from chat context
        
    Returns:
        Natural language comparison response
    """
    logger.info(f"Processing comparative query: {query}")
    
    # Check for special comparison types
    query_lower = query.lower()
    
    # Step 1: Get products to compare
    if context_products and len(context_products) >= 2:
        products_to_compare = context_products
        logger.info(f"Using {len(context_products)} products from chat context")
    else:
        logger.info("No context products, attempting to extract from query")
        df = load_product_database()
        if df.empty:
            return "I don't have access to product information at the moment."
        
        product_series_list = extract_products_for_comparison_enhanced(query, df)
        
        if len(product_series_list) < 2:
            # Special handling for single product queries asking about off-piste vs piste
            if len(product_series_list) == 1 and any(word in query_lower for word in ['more for', 'better for']):
                product = product_series_list[0].to_dict()
                ratings = evaluate_product_flex_ratings(product)
                
                # Compare off-piste vs piste performance
                if 'off' in query_lower and 'piste' in query_lower:
                    off_piste = ratings.get('offpiste_performance', 0.5)
                    piste = ratings.get('piste_performance', 0.5)
                    
                    if off_piste > piste + 0.2:
                        return f"The {product['title']} is more suited for off-piste skiing than piste skiing."
                    elif piste > off_piste + 0.2:
                        return f"The {product['title']} is more suited for piste skiing than off-piste."
                    else:
                        return f"The {product['title']} is well-balanced for both off-piste and piste skiing."
            
            return "I need to know which specific products you'd like me to compare. Could you mention the product names?"
        
        products_to_compare = [p.to_dict() for p in product_series_list[:5]]
        logger.info(f"Found {len(products_to_compare)} products in query")
    
    # Step 2: Check for price comparison
    if any(word in query_lower for word in ['price', 'cost', 'cheap', 'expensive', 'how much']):
        logger.info("Detected price comparison query")
        products_data = [{'info': product, 'ratings': {}} for product in products_to_compare]
        return compare_products_by_price(products_data)
    
    # Step 3: Check for length/height constraint
    height = extract_height_from_query(query)
    if height:
        logger.info(f"Detected height constraint: {height}cm")
        # Extract max over height if specified
        max_over = 5  # default
        
        # Look for explicit "more than X cm" pattern
        over_match = re.search(r'more\s+than\s+(\d+)\s*cm', query_lower)
        if over_match:
            max_over = int(over_match.group(1))
        
        products_data = [{'info': product, 'ratings': {}} for product in products_to_compare]
        return compare_products_by_length_constraint(products_data, height, max_over)
    
    # Step 4: Regular performance comparison
    intent_tags = extract_comparison_intent_tags(query)
    logger.info(f"Extracted intent tags: {intent_tags}")
    
    rating_aspects = map_intent_tags_to_rating_aspects(intent_tags)
    logger.info(f"Comparing aspects: {rating_aspects}")
    
    # Calculate flex ratings for each product
    products_data = []
    for product in products_to_compare:
        ratings = evaluate_product_flex_ratings(product)
        products_data.append({
            'info': product,
            'ratings': ratings
        })
    
    # Compare products across relevant aspects
    comparison_data = compare_products_by_aspects(products_data, rating_aspects)
    
    # Use LLM to interpret comparison
    api_key = get_api_key()
    response = interpret_comparison_fast(query, comparison_data, intent_tags, api_key)
    
    logger.info("Comparison completed successfully")
    return response

def handle_comparative_query(query: str) -> str:
    """
    Handle a comparative property query (backward compatibility wrapper).
    
    Args:
        query: The original query that was classified as comparative
        
    Returns:
        Natural language comparison response
    """
    return handle_comparative_query_with_context(query, context_products=None)

def main():
    """Main function for testing."""
    # Test with simulated context products
    test_context_products = [
        {
            'title': 'Atomic Bent 110',
            'category': 'Freeride',
            'waist_width_mm': 110,
            'tags': 'off-piste, powder, freeride, freestyle'
        },
        {
            'title': 'K2 Mindbender 108',
            'category': 'Freeride',
            'waist_width_mm': 108,
            'tags': 'all-mountain, freeride, touring'
        }
    ]
    
    test_queries = [
        "Which ski is best for off-piste?",
        "Compare these for stability",
        "Which one is better for beginners?",
        "Which is lighter for touring?"
    ]
    
    print("🎿 TESTING COMPARATIVE QUERY HANDLER")
    print("=" * 60)
    print(f"Context products: {[p['title'] for p in test_context_products]}")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        # Show intent extraction
        intent_tags = extract_comparison_intent_tags(query)
        print(f"Intent tags: {intent_tags}")
        
        # Get response
        result = handle_comparative_query_with_context(query, test_context_products)
        print(f"Response: {result}")

if __name__ == "__main__":
    main() 