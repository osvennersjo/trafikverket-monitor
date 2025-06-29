#!/usr/bin/env python3
"""
Property Question System - Main Integration

This module connects all property question components:
1. decide_property_intent - Classifies queries
2. if_comparative - Handles comparative queries
3. if_describing - Handles descriptive queries
4. if_general - Handles general queries
"""

import logging
import time
from typing import Optional, Dict, List

# Import the classifier
from decide_property_intent import decide_property_intent

# Import the handlers
from if_comparative import handle_comparative_query_with_context
from if_describing import handle_describing_query_with_context
from if_general import handle_general_query

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PropertyQuestionSystem:
    """Main system for handling property questions."""
    
    def __init__(self):
        """Initialize the property question system."""
        logger.info("Property Question System initialized")
    
    def process_query(self, 
                     query: str, 
                     context_product: Optional[Dict] = None,
                     context_products: Optional[List[Dict]] = None) -> Dict[str, str]:
        """
        Process a property question through the complete pipeline.
        
        Args:
            query: The user's question
            context_product: Optional single product context (for describing queries)
            context_products: Optional multiple products context (for comparative queries)
            
        Returns:
            Dictionary with:
                - intent: The classified intent
                - response: The generated response
                - processing_time: Time taken to process
        """
        start_time = time.time()
        
        # Step 1: Classify the intent
        intent_result = decide_property_intent(query)
        logger.info(f"Query: '{query}' -> Intent: {intent_result}")
        
        # Step 2: Route to appropriate handler
        if "compare" in intent_result:
            response = handle_comparative_query_with_context(query, context_products)
        elif "describe" in intent_result:
            response = handle_describing_query_with_context(query, context_product)
        elif "general" in intent_result:
            response = handle_general_query(query)
        else:
            response = "I'm unable to understand the type of property question you're asking."
            logger.error(f"Unknown intent result: {intent_result}")
        
        processing_time = time.time() - start_time
        
        return {
            "intent": intent_result,
            "response": response,
            "processing_time": f"{processing_time:.3f}s"
        }

    def process_query_with_intent(self, 
                                 query: str, 
                                 intent: str,
                                 context_product: Optional[Dict] = None,
                                 context_products: Optional[List[Dict]] = None) -> Dict[str, str]:
        """
        Process a property question with pre-classified intent (optimized version).
        
        Args:
            query: The user's question
            intent: Pre-classified intent (e.g., "query=property;describe")
            context_product: Optional single product context (for describing queries)
            context_products: Optional multiple products context (for comparative queries)
            
        Returns:
            Dictionary with:
                - intent: The provided intent
                - response: The generated response
                - processing_time: Time taken to process
        """
        start_time = time.time()
        
        logger.info(f"Processing query with pre-classified intent: {intent}")
        
        # Route to appropriate handler based on intent
        if "compare" in intent:
            response = handle_comparative_query_with_context(query, context_products)
        elif "describe" in intent:
            response = handle_describing_query_with_context(query, context_product)
        elif "general" in intent:
            response = handle_general_query(query)
        else:
            response = "I'm unable to understand the type of property question you're asking."
            logger.error(f"Unknown intent: {intent}")
        
        processing_time = time.time() - start_time
        
        return {
            "intent": intent,
            "response": response,
            "processing_time": f"{processing_time:.3f}s"
        }

def run_interactive_test():
    """Run an interactive test session."""
    system = PropertyQuestionSystem()
    
    print("\n🎿 PROPERTY QUESTION SYSTEM - INTERACTIVE TEST")
    print("=" * 60)
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        print("\n")
        query = input("Enter your question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        print("\nProcessing...")
        result = system.process_query(query)
        
        print(f"\n📋 Intent: {result['intent']}")
        print(f"⏱️  Time: {result['processing_time']}")
        print(f"\n💬 Response:")
        print("-" * 60)
        print(result['response'])
        print("-" * 60)

def run_automated_test():
    """Run automated tests with predefined queries."""
    system = PropertyQuestionSystem()
    
    # Define test cases
    test_cases = [
        # Comparative queries
        {
            "query": "Which ski is better for off-piste, Atomic Bent 110 or K2 Mindbender?",
            "expected_intent": "compare",
            "context_products": [
                {'title': 'Atomic Bent 110', 'tags': 'off-piste, powder, freeride'},
                {'title': 'K2 Mindbender 108', 'tags': 'all-mountain, versatile'}
            ]
        },
        {
            "query": "Compare these skis for stability",
            "expected_intent": "compare"
        },
        
        # Descriptive queries
        {
            "query": "Will this ski work for off-piste?",
            "expected_intent": "describe",
            "context_product": {'title': 'Atomic Bent 110', 'tags': 'off-piste, powder'}
        },
        {
            "query": "Is this good for beginners?",
            "expected_intent": "describe"
        },
        {
            "query": "How stable are these skis?",
            "expected_intent": "describe"
        },
        
        # General queries
        {
            "query": "What should I think about when choosing skis?",
            "expected_intent": "general"
        },
        {
            "query": "Do I need waterproof ski gear?",
            "expected_intent": "general"
        },
        {
            "query": "What makes a good ski jacket?",
            "expected_intent": "general"
        }
    ]
    
    print("\n🧪 PROPERTY QUESTION SYSTEM - AUTOMATED TEST")
    print("=" * 60)
    
    total_time = 0
    correct_intents = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Query: '{test['query']}'")
        print("-" * 60)
        
        # Process the query
        result = system.process_query(
            test['query'],
            context_product=test.get('context_product'),
            context_products=test.get('context_products')
        )
        
        # Check intent accuracy
        expected_intent = f"query=property;{test['expected_intent']}"
        intent_correct = result['intent'] == expected_intent
        if intent_correct:
            correct_intents += 1
        
        # Display results
        print(f"Expected Intent: {expected_intent}")
        print(f"Actual Intent: {result['intent']} {'✅' if intent_correct else '❌'}")
        print(f"Processing Time: {result['processing_time']}")
        print(f"\nResponse: {result['response'][:150]}{'...' if len(result['response']) > 150 else ''}")
        
        total_time += float(result['processing_time'][:-1])  # Remove 's' suffix
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print(f"Total tests: {len(test_cases)}")
    print(f"Intent accuracy: {correct_intents}/{len(test_cases)} ({correct_intents/len(test_cases)*100:.0f}%)")
    print(f"Average processing time: {total_time/len(test_cases):.3f}s")
    print("=" * 60)

def main():
    """Main function with menu."""
    print("\n🎿 PROPERTY QUESTION SYSTEM")
    print("=" * 60)
    print("1. Run automated tests")
    print("2. Interactive mode")
    print("3. Quick demo")
    print("=" * 60)
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        run_automated_test()
    elif choice == "2":
        run_interactive_test()
    elif choice == "3":
        # Quick demo
        system = PropertyQuestionSystem()
        demo_queries = [
            "Which ski is better for powder?",
            "Is this ski good for beginners?",
            "What should I look for in ski boots?"
        ]
        
        print("\n🎯 QUICK DEMO")
        print("=" * 60)
        
        for query in demo_queries:
            print(f"\n❓ {query}")
            result = system.process_query(query)
            print(f"📋 Intent: {result['intent']}")
            print(f"💬 {result['response'][:100]}...")
            print("-" * 40)
    else:
        print("Invalid choice. Please run again.")

if __name__ == "__main__":
    main() 