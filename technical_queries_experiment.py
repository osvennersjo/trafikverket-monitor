#!/usr/bin/env python3
"""
Technical Skiing Queries Experiment - WITH LLM INTERPRETATION
Tests the system with complex, technical skiing questions about specific ski models.
NOW INCLUDES: Final LLM interpretation step that transforms technical data into useful, everyday speech!
"""

import time
from fixed_optimized_query_system import FixedOptimizedQueryHandler

def run_technical_queries_experiment():
    """Run the technical skiing queries experiment with LLM interpretation analysis."""
    
    print("🎿 TECHNICAL SKIING QUERIES EXPERIMENT - WITH LLM INTERPRETATION")
    print("=" * 90)
    print("Testing complex, technical skiing questions about specific ski models")
    print("🧠 NEW FEATURE: LLM interpretation transforms technical specs into useful everyday answers!")
    print("=" * 90)
    
    handler = FixedOptimizedQueryHandler()
    
    # The 10 technical queries
    technical_queries = [
        "Can the Armada Declivity 92 Ti 25/26 handle steep, technical lines off-piste?",
        "Is the Head Supershape i.Magnum 24/25 suited for high-speed carving on icy groomers?",
        "Would the Fischer Transalp 98 CTI 23/24 be a good choice for extended backcountry touring days?",
        "Is the Nordica Santa Ana 93 24/25 forgiving enough for a progression-focused beginner on all-mountain terrain?",
        "Does the Blizzard Rustler 11 24/25 have the pop and flex needed for freestyle park laps?",
        "Which ski would float better in deep powder: the DPS Wailer 112 RP 24/25 or the Völkl Blaze 106 24/25?",
        "Between the Salomon QST Lux 92 Ti 24/25 and the Rossignol Soul 7 HD 24/25, which offers more versatility across mixed snow conditions?",
        "For tight, slalom-style carving, which performs more responsively: the Head Supershape i.Magnum 24/25 or the Atomic Maverick 105 CTi 25/26?",
        "Which holds an edge more securely on hard, icy slopes: the Nordica Enforcer 93 24/25 or the Line Vision 114 Camo 24/25?",
        "For long days skinning uphill, which is better suited: the Salomon Départ 1.0 or the Fischer Transalp 98 CTI 23/24?"
    ]
    
    results = []
    total_time = 0
    
    for i, query in enumerate(technical_queries, 1):
        print(f"\n{'='*80}")
        print(f"TECHNICAL QUERY {i}/10:")
        print(f"{query}")
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
            'success': products_found > 0 or result.intent in ['compare', 'describe']
        })
        
        # Display detailed results
        print(f"Intent: {result.intent}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Response Time: {response_time:.3f} seconds")
        print(f"Products Found: {products_found}")
        
        if result.error_message:
            print(f"Error: {result.error_message}")
        
        print(f"\n📝 EXACT FINAL OUTPUT:")
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
    
    # Generate comprehensive analysis
    print(f"\n{'='*80}")
    print("📊 TECHNICAL QUERIES EXPERIMENT ANALYSIS")
    print('='*80)
    
    # Overall performance stats
    successful_queries = sum(1 for r in results if r['success'])
    success_rate = (successful_queries / len(technical_queries)) * 100
    avg_time = total_time / len(technical_queries)
    
    print(f"📈 OVERALL PERFORMANCE:")
    print(f"   Total technical queries: {len(technical_queries)}")
    print(f"   Successful queries: {successful_queries}")
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Total processing time: {total_time:.3f} seconds")
    print(f"   Average response time: {avg_time:.3f} seconds")
    
    # Intent classification breakdown
    intent_counts = {}
    intent_times = {}
    for r in results:
        intent = r['intent']
        if intent not in intent_counts:
            intent_counts[intent] = 0
            intent_times[intent] = 0
        intent_counts[intent] += 1
        intent_times[intent] += r['response_time']
    
    print(f"\n🔍 INTENT CLASSIFICATION BREAKDOWN:")
    for intent, count in intent_counts.items():
        avg_time_intent = intent_times[intent] / count
        print(f"   {intent}: {count} queries (avg {avg_time_intent:.3f}s)")
    
    # Timing analysis
    fastest = min(results, key=lambda x: x['response_time'])
    slowest = max(results, key=lambda x: x['response_time'])
    
    print(f"\n⏱️  TIMING ANALYSIS:")
    print(f"   Fastest query: {fastest['response_time']:.3f}s (Query {fastest['query_num']})")
    print(f"   Slowest query: {slowest['response_time']:.3f}s (Query {slowest['query_num']})")
    
    # Query complexity analysis
    print(f"\n🧠 QUERY COMPLEXITY ANALYSIS:")
    compare_queries = [r for r in results if r['intent'] == 'compare']
    describe_queries = [r for r in results if r['intent'] == 'describe']
    general_queries = [r for r in results if r['intent'] == 'general']
    
    if compare_queries:
        avg_compare_time = sum(r['response_time'] for r in compare_queries) / len(compare_queries)
        print(f"   Comparison queries: {len(compare_queries)} (avg {avg_compare_time:.3f}s)")
    
    if describe_queries:
        avg_describe_time = sum(r['response_time'] for r in describe_queries) / len(describe_queries)
        print(f"   Description queries: {len(describe_queries)} (avg {avg_describe_time:.3f}s)")
    
    if general_queries:
        avg_general_time = sum(r['response_time'] for r in general_queries) / len(general_queries)
        print(f"   General queries: {len(general_queries)} (avg {avg_general_time:.3f}s)")
    
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
    
    # Individual query performance
    print(f"\n🔍 INDIVIDUAL QUERY PERFORMANCE:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"   {status} Q{r['query_num']}: {r['intent']} | {r['response_time']:.3f}s | {r['products_found']} products")
    
    # Technical query specific analysis
    print(f"\n🎿 TECHNICAL SKIING ANALYSIS:")
    
    # Categorize by skiing discipline
    off_piste_queries = [r for r in results if any(term in r['query'].lower() for term in ['off-piste', 'powder', 'backcountry'])]
    carving_queries = [r for r in results if any(term in r['query'].lower() for term in ['carving', 'icy', 'groomers', 'edge'])]
    park_queries = [r for r in results if any(term in r['query'].lower() for term in ['park', 'freestyle', 'pop', 'flex'])]
    
    print(f"   Off-piste/Powder queries: {len(off_piste_queries)}")
    print(f"   Carving/Groomer queries: {len(carving_queries)}")
    print(f"   Park/Freestyle queries: {len(park_queries)}")
    
    # Final assessment
    print(f"\n🎉 FINAL TECHNICAL QUERIES ASSESSMENT:")
    if success_rate >= 80:
        print(f"   🟢 EXCELLENT: {success_rate:.1f}% success rate on technical queries")
    elif success_rate >= 60:
        print(f"   🟡 GOOD: {success_rate:.1f}% success rate on technical queries")
    else:
        print(f"   🔴 NEEDS IMPROVEMENT: {success_rate:.1f}% success rate on technical queries")
    
    if avg_time <= 0.05:
        print(f"   🟢 EXCELLENT SPEED: {avg_time:.3f}s average for technical queries")
    elif avg_time <= 0.1:
        print(f"   🟡 GOOD SPEED: {avg_time:.3f}s average for technical queries")
    else:
        print(f"   🔴 SLOW: {avg_time:.3f}s average for technical queries")
    
    print(f"\n🏆 EXPERIMENT CONCLUSION:")
    print(f"   The system handled {len(technical_queries)} complex technical skiing queries")
    print(f"   with {success_rate:.1f}% success rate and {avg_time:.3f}s average response time.")
    if success_rate >= 70 and avg_time <= 0.1:
        print("   🎿 READY FOR EXPERT SKIER CONSULTATIONS!")
    else:
        print("   ⚠️  May need further optimization for complex technical queries.")

if __name__ == "__main__":
    run_technical_queries_experiment() 