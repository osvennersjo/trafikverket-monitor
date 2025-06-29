#!/usr/bin/env python3
"""
Query Handler - Main Integration

This module integrates user intent classification with the property question system.
It routes queries through the appropriate pipeline:
1. First classifies as "search query" or "property query"
2. If property query, routes through the property question system
3. Returns the appropriate response
"""

import logging
import sys
import os
from typing import Dict, Optional, Literal

# Import the intent classifiers
try:
    from user_intent_final_comb import get_intent as get_intent_gemini, get_api_key as get_gemini_key
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from user_intent_final import get_intent as get_intent_openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import the property question system
sys.path.append('answer_product_question')
from property_question_system import PropertyQuestionSystem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryHandler:
    """Main query handler that routes queries through the appropriate pipeline."""
    
    def __init__(self, classifier: Literal["gemini", "openai", "auto"] = "auto"):
        """
        Initialize the query handler.
        
        Args:
            classifier: Which intent classifier to use ("gemini", "openai", or "auto")
        """
        self.classifier = self._select_classifier(classifier)
        self.property_system = PropertyQuestionSystem()
        logger.info(f"QueryHandler initialized with {self.classifier} classifier")
    
    def _select_classifier(self, preference: str) -> str:
        """Select the appropriate classifier based on availability and preference."""
        if preference == "gemini" and GEMINI_AVAILABLE:
            return "gemini"
        elif preference == "openai" and OPENAI_AVAILABLE:
            return "openai"
        elif preference == "auto":
            # Prefer Gemini if available (it's free)
            if GEMINI_AVAILABLE:
                return "gemini"
            elif OPENAI_AVAILABLE:
                return "openai"
            else:
                raise ImportError("No intent classifier available. Please ensure user_intent_final.py or user_intent_final_comb.py is present.")
        else:
            raise ValueError(f"Classifier '{preference}' not available.")
    
    def classify_intent(self, query: str) -> str:
        """
        Classify the user's intent.
        
        Args:
            query: The user's query
            
        Returns:
            "search query" or "property query"
        """
        if self.classifier == "gemini":
            api_key = get_gemini_key()
            return get_intent_gemini(query, api_key)
        else:  # openai
            return get_intent_openai(query)
    
    def handle_query(self, query: str) -> Dict[str, any]:
        """
        Handle a user query end-to-end.
        
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
            # Step 1: Classify intent
            intent = self.classify_intent(query)
            logger.info(f"Query classified as: {intent}")
            
            if intent == "property query":
                # Step 2: Route through property question system
                result = self.property_system.process_query(query)
                return {
                    "intent": intent,
                    "property_intent": result.get("intent"),
                    "response": result.get("response"),
                    "status": "success"
                }
            else:
                # Search query - return intent only (search handling not implemented here)
                return {
                    "intent": intent,
                    "response": None,
                    "status": "success",
                    "message": "Search queries should be routed to the search system"
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
        description="Handle user queries through intent classification and property question system"
    )
    parser.add_argument("query", nargs="?", help="The query to process")
    parser.add_argument("--classifier", choices=["gemini", "openai", "auto"], default="auto",
                       help="Which intent classifier to use (default: auto)")
    parser.add_argument("--interactive", action="store_true", 
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Initialize handler
    try:
        handler = QueryHandler(classifier=args.classifier)
    except Exception as e:
        print(f"❌ Error initializing handler: {e}")
        sys.exit(1)
    
    if args.interactive:
        print("🎯 INTERACTIVE QUERY HANDLER")
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
                result = handler.handle_query(query)
                
                # Display result
                print(f"\n📊 Intent: {result['intent']}")
                if result['intent'] == 'property query':
                    print(f"📋 Property Intent: {result.get('property_intent', 'N/A')}")
                    print(f"\n💬 Response:")
                    print(result['response'])
                else:
                    print("ℹ️  This is a search query - route to search system")
                
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
        result = handler.handle_query(query)
        
        # Display result
        print(f"\nQuery: \"{query}\"")
        print(f"Intent: {result['intent']}")
        
        if result['intent'] == 'property query':
            print(f"Property Intent: {result.get('property_intent', 'N/A')}")
            print(f"\nResponse:")
            print(result['response'])
        else:
            print("\nThis is a search query - should be routed to search system")
        
        if result['status'] == 'error':
            print(f"\nError: {result['message']}")
            sys.exit(1)

if __name__ == "__main__":
    main() 