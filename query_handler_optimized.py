#!/usr/bin/env python3
"""
Optimized Query Handler - Single API Call Version

This optimized version uses the unified intent classifier to reduce API calls
from 2 to 1, cutting costs by 50% and improving response time by ~0.5 seconds.
"""

import logging
import sys
import os
from typing import Dict, Optional, Literal

# Import the unified classifier
from unified_intent_classifier import get_unified_intent, get_api_key

# Import the property question system
sys.path.append('answer_product_question')
from property_question_system import PropertyQuestionSystem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedQueryHandler:
    """Optimized query handler that uses unified classification."""
    
    def __init__(self):
        """Initialize the optimized query handler."""
        self.property_system = PropertyQuestionSystem()
        self.api_key = get_api_key()
        logger.info("OptimizedQueryHandler initialized with unified classifier")
    
    def handle_query(self, query: str) -> Dict[str, any]:
        """
        Handle a user query with optimized single-API-call classification.
        
        Args:
            query: The user's query
            
        Returns:
            Dictionary with:
            - intent: The classified intent
            - response: The response (for property queries) or None (for search queries)
            - status: "success" or "error"
            - message: Any error message
        """
        try:
            # Single API call for full classification
            classification = get_unified_intent(query, self.api_key)
            logger.info(f"Query classified as: {classification}")
            
            if classification == "search query":
                # Search query - return intent only
                return {
                    "intent": "search query",
                    "response": None,
                    "status": "success",
                    "message": "Search queries should be routed to the search system"
                }
            else:
                # Property query - route through property question system
                # Create a mock result with the pre-classified intent
                property_intent = classification  # Already in format "query=property;type"
                
                # Route through the proper property question system
                # We'll override the classification in the property system
                result = self.property_system.process_query_with_intent(query, property_intent)
                
                return {
                    "intent": "property query",
                    "property_intent": property_intent,
                    "response": result.get("response"),
                    "status": "success"
                }
                
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            return {
                "intent": None,
                "response": None,
                "status": "error",
                "message": str(e)
            }

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Optimized query handler with single API call classification"
    )
    parser.add_argument("query", nargs="?", help="The query to process")
    parser.add_argument("--interactive", action="store_true", 
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Initialize handler
    try:
        handler = OptimizedQueryHandler()
    except Exception as e:
        print(f"❌ Error initializing handler: {e}")
        sys.exit(1)
    
    if args.interactive:
        print("🎯 OPTIMIZED QUERY HANDLER (Single API Call)")
        print("=" * 60)
        print("Enter queries to process (type 'exit' to quit)")
        print("=" * 60)
        
        while True:
            try:
                query = input("\n> ").strip()
                if query.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                    
                if not query:
                    continue
                
                # Process query
                import time
                start_time = time.time()
                result = handler.handle_query(query)
                elapsed = time.time() - start_time
                
                # Display result
                print(f"\n📊 Intent: {result.get('intent', 'N/A')}")
                if result.get('property_intent'):
                    print(f"📋 Property Intent: {result['property_intent']}")
                    
                if result['intent'] == 'property query':
                    print(f"\n💬 Response:")
                    print(result['response'])
                else:
                    print("ℹ️  This is a search query - route to search system")
                
                print(f"\n⏱️  Response Time: {elapsed:.2f} seconds")
                
                if result['status'] == 'error':
                    print(f"\n❌ Error: {result['message']}")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
    else:
        # Single query mode
        query = args.query
        if not query:
            query = input("Enter query: ").strip()
        
        if not query:
            print("No query provided")
            sys.exit(1)
        
        # Process query
        import time
        start_time = time.time()
        result = handler.handle_query(query)
        elapsed = time.time() - start_time
        
        # Display result
        print(f"\nQuery: \"{query}\"")
        print(f"Intent: {result.get('intent', 'N/A')}")
        
        if result.get('property_intent'):
            print(f"Property Intent: {result['property_intent']}")
            
        if result['intent'] == 'property query':
            print(f"\nResponse:")
            print(result['response'])
        else:
            print("\nThis is a search query - should be routed to search system")
        
        print(f"\nResponse Time: {elapsed:.2f} seconds")
        
        if result['status'] == 'error':
            print(f"\nError: {result['message']}")
            sys.exit(1)

if __name__ == "__main__":
    main() 