#!/usr/bin/env python3
"""
Test specific queries requested by the user with exact output and timing
"""

import time
from fixed_optimized_query_system import FixedOptimizedQueryHandler

def test_specific_queries():
    """Test the specific queries and show exact output with timing."""
    
    print("🔍 TESTING SPECIFIC QUERIES WITH EXACT OUTPUT & TIMING")
    print("=" * 80)
    
    handler = FixedOptimizedQueryHandler()
    
    # List of queries to test
    queries = [
        "What's the waist width of the Faction Prodigy 4 24/25?",
        "How much does the DPS Wailer 112 RP 24/25 cost?",
        "What's the listed price for the Nordica Santa Ana 93 24/25?",
        "Is the Salomon QST Lux 92 Ti 24/25 a twin-tip ski?",
        "Which length options are offered for the Armada ARV 88 24/25?",
        "Between the Atomic Bent Chetler 120 NRX 24/25 and the Blizzard Rustler 11 24/25, which ski is wider?",
        "Which has a wider waist: the Völkl Blaze 106 24/25 or the Line Vision 114 Camo 24/25?",
        "Comparing the Salomon Départ 1.0 and the Fischer Transalp 98 CTI 23/24, which model comes in more length options?",
        "For the Rossignol Soul 7 HD 24/25, does its waist width put it in the 'medium' or 'wide' category?",
        "Which is more expensive: the Head Supershape i.Magnum 24/25 or the Atomic Maverick 105 CTi 25/26?"
    ]
    
    total_time = 0
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY {i}: {query}")
        print('='*80)
        
        # Measure response time
        start_time = time.time()
        result = handler.handle_query(query)
        end_time = time.time()
        response_time = end_time - start_time
        total_time += response_time
        
        # Store results
        results.append({
            'query': query,
            'intent': result.intent,
            'confidence': result.confidence,
            'response_time': response_time,
            'response': result.response,
            'matched_products': len(result.matched_products) if result.matched_products else 0,
            'error': result.error_message
        })
        
        # Display results
        print(f"Intent: {result.intent}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Response Time: {response_time:.3f} seconds")
        print(f"Products Found: {len(result.matched_products) if result.matched_products else 0}")
        
        if result.error_message:
            print(f"Error: {result.error_message}")
        
        print(f"\nFULL RESPONSE:")
        print("-" * 60)
        print(result.response)
        print("-" * 60)
        
        if result.matched_products:
            print(f"\nMATCHED PRODUCTS:")
            for j, product in enumerate(result.matched_products[:3], 1):
                title = product.get('title', 'Unknown')
                waist = product.get('waist_width_mm', 'N/A')
                price = product.get('price', 'N/A')
                print(f"  {j}. {title} - Waist: {waist}mm - Price: {price} SEK")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY RESULTS")
    print('='*80)
    
    avg_time = total_time / len(queries)
    print(f"Total queries processed: {len(queries)}")
    print(f"Total processing time: {total_time:.3f} seconds")
    print(f"Average response time: {avg_time:.3f} seconds")
    
    # Performance breakdown
    intent_breakdown = {}
    for result in results:
        intent = result['intent']
        if intent not in intent_breakdown:
            intent_breakdown[intent] = {'count': 0, 'total_time': 0}
        intent_breakdown[intent]['count'] += 1
        intent_breakdown[intent]['total_time'] += result['response_time']
    
    print(f"\nPERFORMANCE BY INTENT:")
    for intent, data in intent_breakdown.items():
        avg_time_intent = data['total_time'] / data['count']
        print(f"  {intent}: {data['count']} queries, avg {avg_time_intent:.3f}s")
    
    # Success rate
    successful_queries = sum(1 for r in results if r['matched_products'] > 0 or r['intent'] in ['compare', 'describe'])
    success_rate = (successful_queries / len(queries)) * 100
    print(f"\nSuccess rate: {successful_queries}/{len(queries)} ({success_rate:.1f}%)")
    
    # Fastest and slowest
    fastest = min(results, key=lambda x: x['response_time'])
    slowest = max(results, key=lambda x: x['response_time'])
    
    print(f"\nFastest query: {fastest['response_time']:.3f}s")
    print(f"Slowest query: {slowest['response_time']:.3f}s")

if __name__ == "__main__":
    test_specific_queries() 