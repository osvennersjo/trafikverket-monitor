#!/usr/bin/env python3
"""
Test the Stöckli Laser MX specific query handling
"""

from fixed_optimized_query_system import FixedOptimizedQueryHandler

def test_stockli_laser():
    """Test Stöckli Laser MX for off-piste query."""
    
    handler = FixedOptimizedQueryHandler()
    
    # Check if we can find Stöckli products
    print("🔍 TESTING STÖCKLI LASER MX QUERY")
    print("=" * 50)
    
    # Test with different variations
    queries = [
        "Can I use the Stöckli Laser MX for off piste?",
        "What are the specs of the Stöckli Laser MX?",
        "Is the Stöckli Laser good for powder?",
        "Show me Stöckli skis"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        result = handler.handle_query(query)
        print(f"Intent: {result.intent}")
        print(f"Confidence: {result.confidence}")
        
        if result.matched_products:
            print(f"Products found: {len(result.matched_products)}")
            for j, product in enumerate(result.matched_products[:2], 1):
                title = product.get('title', 'Unknown')
                waist = product.get('waist_width_mm', 'N/A')
                print(f"  {j}. {title} - Waist: {waist}mm")
        else:
            print("No products found")
        
        print(f"Response: {result.response[:150]}...")

if __name__ == "__main__":
    test_stockli_laser() 