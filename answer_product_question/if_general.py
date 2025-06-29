#!/usr/bin/env python3
"""
If General - Handler for General Property Queries

This file handles queries classified as "query=property;general"
General queries are advice-seeking questions about properties or requirements.

Examples:
- "Do I need waterproof shoes for hiking?"
- "What should I look for in hiking boots?"
- "How do I choose the right ski length?"
- "What makes a good winter jacket?"
"""

import os
import sys
import logging
import pandas as pd
from typing import Optional
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
CSV_FILE_PATH = "brand_information.csv"
FALLBACK_API_KEY = "AIzaSyAOYbQD5dAAQsYyK4lfFp-ciiXJgj3prCw"

def get_api_key() -> str:
    """Get Gemini API key from environment or fallback."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        logger.info("Using Gemini API key from environment variable.")
        return api_key
    
    logger.warning("Using fallback API key.")
    return FALLBACK_API_KEY

def load_brand_database() -> pd.DataFrame:
    """
    Load the brand information database from CSV file.
    
    Returns:
        DataFrame with brand information or empty DataFrame if file not found
    """
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        logger.info(f"Loaded {len(df)} brands from CSV database")
        return df
    except FileNotFoundError:
        logger.error(f"Database file not found: {CSV_FILE_PATH}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading database: {e}")
        return pd.DataFrame()

def search_relevant_brands(query: str, df: pd.DataFrame) -> str:
    """
    Search for relevant brand information based on the query.
    
    Args:
        query: The user's query
        df: DataFrame with brand information
        
    Returns:
        Relevant brand information as a string
    """
    if df.empty:
        return ""
    
    # Convert query to lowercase for matching
    query_lower = query.lower()
    
    # Keywords that might indicate specific brand interest
    brand_keywords = []
    for brand in df['brand'].str.lower():
        if brand in query_lower:
            brand_keywords.append(brand)
    
    # If specific brands mentioned, return their info
    if brand_keywords:
        relevant_info = []
        for brand in brand_keywords:
            brand_row = df[df['brand'].str.lower() == brand]
            if not brand_row.empty:
                info = brand_row.iloc[0]
                relevant_info.append(f"**{info['brand']}**: {info['information']}")
        return "\n\n".join(relevant_info)
    
    # Otherwise, return all brand information for general context
    all_info = []
    for _, row in df.iterrows():
        all_info.append(f"**{row['brand']}**: {row['information']}")
    
    return "\n\n".join(all_info)

def query_gemini_with_context(query: str, context: str, api_key: str) -> Optional[str]:
    """
    Query Gemini API with brand context to answer the general question.
    
    Args:
        query: The user's original query
        context: Relevant brand information from database
        api_key: Gemini API key
        
    Returns:
        Gemini's response or None if API fails
    """
    try:
        genai.configure(api_key=api_key)
        
        prompt = f"""
You are an expert ski equipment advisor. Answer the user's question using the provided brand information database.

BRAND DATABASE:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. For questions starting with "Do", "Should", "Is", "Are", "Would", "Can" - BEGIN your response with "Yes" or "No" followed by your explanation
2. Use ONLY the information provided in the brand database above
3. If the database contains relevant information to answer the question, provide a helpful response
4. If the database does NOT contain sufficient information to answer the question, respond with exactly: "I have no information on that"
5. Be specific and reference the brands when relevant
6. Keep the response concise but informative
7. Focus on practical advice based on the available brand data

RESPONSE:
"""

        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return None

def handle_general_query(query: str) -> str:
    """
    Handle a general property query using brand database and Gemini API.
    
    Args:
        query: The original query that was classified as general
        
    Returns:
        Response based on brand database or "I have no information on that"
    """
    logger.info(f"Processing general query: {query}")
    
    # Load brand database
    df = load_brand_database()
    if df.empty:
        return "I have no information on that"
    
    # Search for relevant brand information
    context = search_relevant_brands(query, df)
    if not context:
        return "I have no information on that"
    
    # Get API key and query Gemini
    api_key = get_api_key()
    response = query_gemini_with_context(query, context, api_key)
    
    if response is None:
        return "I have no information on that"
    
    # Check if Gemini explicitly said no information
    if "I have no information on that" in response:
        return "I have no information on that"
    
    return response

def main():
    """Main function for testing."""
    test_queries = [
        "What should I look for in ski equipment?",
        "Which brand is best for slalom skiing?",
        "Do I need special skis for powder snow?",
        "What makes a good winter jacket?",  # This should return "I have no information on that"
        "Tell me about Atomic skis",
        "Which brands focus on extreme skiing?",
        "How do I choose the right ski brand?",
        "What about mountain climbing gear?"  # This should return "I have no information on that"
    ]
    
    print("🧪 TESTING GENERAL QUERY HANDLER")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: \"{query}\"")
        print("-" * 40)
        result = handle_general_query(query)
        print(f"Response: {result}")
        print()

if __name__ == "__main__":
    main() 