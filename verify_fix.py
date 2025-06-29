#!/usr/bin/env python3
"""
Verify the fix works with the optimized query handler
"""

import time
from query_handler_optimized import OptimizedQueryHandler

# The query that was misclassified
query = "Between the Line Pandora 99 and the Line Chronic 94, which has a lighter weight and tighter turn radius for quick tree runs?"

print("🧪 VERIFYING FIX FOR 'BETWEEN X AND Y' PATTERN")
print("=" * 60)
print(f"Query: {query}")
print("=" * 60)

# Test with optimized handler
handler = OptimizedQueryHandler()
start_time = time.time()
result = handler.handle_query(query)
elapsed = time.time() - start_time

print(f"\nIntent: {result['intent']}")
print(f"Property Intent: {result.get('property_intent', 'N/A')}")
print(f"Response Time: {elapsed:.2f}s")
print(f"\nResponse Preview: {result.get('response', 'No response')[:150]}...")

# Check if it's correctly classified
expected_property = "query=property;compare"
if result.get('property_intent') == expected_property:
    print("\n✅ SUCCESS: Query correctly classified as compare!")
else:
    print(f"\n❌ FAILED: Expected {expected_property}, got {result.get('property_intent')}") 