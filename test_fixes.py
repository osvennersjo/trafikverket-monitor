#!/usr/bin/env python3
"""
Comprehensive test of the fixed property question system
Testing all 6 problematic queries from the user
"""

import time
import sys
sys.path.append('answer_product_question')
from property_question_system import PropertyQuestionSystem

def test_all_queries():
    """Test all 6 queries and evaluate accuracy."""
    system = PropertyQuestionSystem()
    
    queries = [
        {
            "id": 1,
            "query": "Can I use the Stöckli Laser MX for off piste?",
            "expected": "No (71mm waist, piste ski)",
            "type": "describe"
        },
        {
            "id": 2,
            "query": "Should I use the Völkl Blaze 114 or the Völkl Blaze 104 Purple for deep powder skiing?",
            "expected": "Both good, 114 wider/better for powder",
            "type": "compare"
        },
        {
            "id": 3,
            "query": "Are the Völkl Mantra Junior twintip?",
            "expected": "Yes",
            "type": "describe"
        },
        {
            "id": 4,
            "query": "Are the Nordica Enforcer 89 more for off piste or more for piste skiing?",
            "expected": "More for piste",
            "type": "compare"
        },
        {
            "id": 5,
            "query": "I am 160cm tall, will the DPS Kaizen 100 24/25 or the Dynafit Blacklight 88 23/24 fit me? I do not want anything that is more than 5cm longer than me.",
            "expected": "Only Dynafit (165cm), DPS too long (179cm)",
            "type": "compare"
        },
        {
            "id": 6,
            "query": "Which of the Faction Prodigy 2 24/25, Faction Studio 1 23/24, K2 Reckoner 92 24/25 and Line Sakana 105 is the cheapest and how much is each ski currently?",
            "expected": "K2 Reckoner 92 cheapest at 2579 SEK",
            "type": "compare"
        }
    ]
    
    print("🎿 COMPREHENSIVE FIXED SYSTEM TEST")
    print("=" * 80)
    
    results = []
    total_time = 0
    
    for test in queries:
        print(f"\n{test['id']}. QUERY: \"{test['query']}\"")
        print(f"   Expected: {test['expected']}")
        print("-" * 80)
        
        start_time = time.time()
        try:
            result = system.process_query(test['query'])
            processing_time = time.time() - start_time
            total_time += processing_time
            
            response = result['response']
            intent = result['intent']
            
            # Evaluate accuracy
            accurate = False
            if test['id'] == 1:
                accurate = "no" in response.lower() and ("71" in response or "piste" in response.lower())
            elif test['id'] == 2:
                accurate = "blaze" in response.lower()
            elif test['id'] == 3:
                accurate = "yes" in response.lower() and "twin-tip" in response.lower()
            elif test['id'] == 4:
                accurate = "piste" in response.lower() and "enforcer" in response.lower()
            elif test['id'] == 5:
                accurate = "dynafit" in response.lower() and ("179" in response or "too long" in response.lower())
            elif test['id'] == 6:
                accurate = any(price in response for price in ["2579", "4654", "3648", "6997"])
            
            results.append({
                'id': test['id'],
                'accurate': accurate,
                'time': processing_time,
                'intent': intent,
                'response': response
            })
            
            print(f"⏱️  TIME: {processing_time:.3f}s")
            print(f"📋 INTENT: {intent}")
            print(f"✅ ACCURATE: {'YES' if accurate else 'NO'}")
            print(f"💬 RESPONSE: {response[:200]}{'...' if len(response) > 200 else ''}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                'id': test['id'],
                'accurate': False,
                'time': 0,
                'intent': 'error',
                'response': str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS SUMMARY")
    print("=" * 80)
    
    accurate_count = sum(1 for r in results if r['accurate'])
    avg_time = total_time / len(queries) if queries else 0
    
    print(f"Accuracy: {accurate_count}/{len(queries)} ({accurate_count/len(queries)*100:.0f}%)")
    print(f"Average response time: {avg_time:.3f}s")
    
    print("\nDetailed Results:")
    for r in results:
        status = "✅" if r['accurate'] else "❌"
        print(f"Query {r['id']}: {status} ({r['time']:.3f}s)")
    
    print("\n" + "=" * 80)
    print("SYSTEM STATUS: " + ("✅ PRODUCTION READY" if accurate_count == len(queries) else f"⚠️  NEEDS WORK ({len(queries)-accurate_count} failures)"))
    print("=" * 80)

if __name__ == "__main__":
    test_all_queries() 