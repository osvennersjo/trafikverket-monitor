#!/usr/bin/env python3
"""
Final comprehensive test of all 10 specific queries with exact output and timing
"""

import time
from fixed_optimized_query_system import FixedOptimizedQueryHandler

def run_comprehensive_test():
    """Run all 10 queries with detailed results and timing."""
    
    print("🎯 FINAL COMPREHENSIVE TEST - ALL 10 QUERIES")
    print("=" * 80)
    
    handler = FixedOptimizedQueryHandler()
    
    # All 10 queries requested
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
    
    results = []
    total_time = 0
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY {i}/10: {query}")
        print('='*80)
        
        # Measure exact timing
        start_time = time.time()
        result = handler.handle_query(query)
        end_time = time.time()
        response_time = end_time - start_time
        total_time += response_time
        
        # Safely handle matched_products
        matched_products = result.matched_products if result.matched_products else []
        products_found = len(matched_products)
        
        # Store results
        results.append({
            'query_num': i,
            'query': query,
            'intent': result.intent,
            'confidence': result.confidence,
            'response_time': response_time,
            'response': result.response,
            'products_found': products_found,
            'success': products_found > 0 or result.intent == 'compare'
        })
        
        # Display detailed results
        print(f"Intent: {result.intent}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Response Time: {response_time:.3f} seconds")
        print(f"Products Found: {products_found}")
        
        if result.error_message:
            print(f"Error: {result.error_message}")
        
        print(f"\n📝 EXACT RESPONSE:")
        print("-" * 60)
        print(result.response)
        print("-" * 60)
        
        # Show matched products if any
        if matched_products:
            print(f"\n🎯 MATCHED PRODUCTS:")
            for j, product in enumerate(matched_products[:2], 1):
                title = product.get('title', 'Unknown')
                waist = product.get('waist_width_mm', 'N/A')
                price = product.get('price', 'N/A')
                score = product.get('match_score', 0)
                print(f"  {j}. {title}")
                print(f"     Waist: {waist}mm | Price: {price} SEK | Score: {score:.2f}")
    
    # Generate comprehensive summary
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE PERFORMANCE ANALYSIS")
    print('='*80)
    
    # Overall stats
    successful_queries = sum(1 for r in results if r['success'])
    success_rate = (successful_queries / len(queries)) * 100
    avg_time = total_time / len(queries)
    
    print(f"📈 OVERALL PERFORMANCE:")
    print(f"   Total queries: {len(queries)}")
    print(f"   Successful queries: {successful_queries}")
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Total processing time: {total_time:.3f} seconds")
    print(f"   Average response time: {avg_time:.3f} seconds")
    
    # Intent breakdown
    intent_counts = {}
    intent_times = {}
    for r in results:
        intent = r['intent']
        if intent not in intent_counts:
            intent_counts[intent] = 0
            intent_times[intent] = 0
        intent_counts[intent] += 1
        intent_times[intent] += r['response_time']
    
    print(f"\n🔍 INTENT CLASSIFICATION:")
    for intent, count in intent_counts.items():
        avg_time_intent = intent_times[intent] / count
        print(f"   {intent}: {count} queries (avg {avg_time_intent:.3f}s)")
    
    # Timing analysis
    fastest = min(results, key=lambda x: x['response_time'])
    slowest = max(results, key=lambda x: x['response_time'])
    
    print(f"\n⏱️  TIMING ANALYSIS:")
    print(f"   Fastest: {fastest['response_time']:.3f}s (Query {fastest['query_num']})")
    print(f"   Slowest: {slowest['response_time']:.3f}s (Query {slowest['query_num']})")
    
    # Success analysis
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✅ SUCCESSFUL QUERIES:")
    for r in successful:
        print(f"   Q{r['query_num']}: {r['intent']} ({r['response_time']:.3f}s) - {r['products_found']} products")
    
    if failed:
        print(f"\n❌ FAILED QUERIES:")
        for r in failed:
            print(f"   Q{r['query_num']}: {r['intent']} - {r['query'][:50]}...")
    
    # Query-by-query breakdown
    print(f"\n🔍 DETAILED QUERY ANALYSIS:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"   {status} Q{r['query_num']}: {r['intent']} | {r['response_time']:.3f}s | {r['products_found']} products")
    
    # Final assessment
    print(f"\n🎉 FINAL ASSESSMENT:")
    if success_rate >= 70:
        print(f"   🟢 EXCELLENT: {success_rate:.1f}% success rate")
    elif success_rate >= 50:
        print(f"   🟡 GOOD: {success_rate:.1f}% success rate")
    else:
        print(f"   🔴 NEEDS IMPROVEMENT: {success_rate:.1f}% success rate")
    
    if avg_time <= 0.1:
        print(f"   🟢 EXCELLENT SPEED: {avg_time:.3f}s average")
    elif avg_time <= 0.5:
        print(f"   🟡 GOOD SPEED: {avg_time:.3f}s average")
    else:
        print(f"   🔴 SLOW: {avg_time:.3f}s average")

if __name__ == "__main__":
    run_comprehensive_test() 