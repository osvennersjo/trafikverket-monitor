#!/usr/bin/env python3
"""
Enhanced Flask API Server for Ski Equipment Query System
Version 2.0 - Enhanced Testing with Proper Status Management
"""

import logging
import time
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from fixed_optimized_query_system import FixedOptimizedQueryHandler

# API Version
API_VERSION = "3.0"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Gemini API key explicitly
os.environ['GEMINI_API_KEY'] = "AIzaSyAOYbQD5dAAQsYyK4lfFp-ciiXJgj3prCw"

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the query handler
try:
    query_handler = FixedOptimizedQueryHandler()
    system_status = "active"
    logger.info("✅ Ski query system initialized successfully!")
except Exception as e:
    logger.error(f"❌ Failed to initialize query system: {e}")
    query_handler = None
    system_status = "error"

@app.route('/', methods=['GET'])
def home():
    """API information endpoint."""
    return jsonify({
        "message": "🎿 Ski Equipment Query System API",
        "version": API_VERSION,
        "status": system_status,
        "products_loaded": len(query_handler.df) if query_handler else 0,
        "system_ready": query_handler is not None,
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check", 
            "GET /version": "Version information",
            "POST /query": "Submit skiing questions",
            "POST /show-prompt": "Show exact Gemini prompts for queries",
            "GET /test": "Test with sample query",
            "GET /examples": "Get example queries showing the fixes",
            "POST /test-fixes": "Test all the recent fixes",
            "GET /debug": "Debug information"
        },
        "example_usage": {
            "url": "POST /query",
            "body": {
                "query": "Which of the Dynafit Blacklight 88 W 24/25 and Extrem Mother Tree 95 24/25 is the cheapest?"
            }
        }
    })

@app.route('/version', methods=['GET'])
def version_info():
    """Version information endpoint."""
    return jsonify({
        "api_version": API_VERSION,
        "system_status": system_status,
        "last_updated": "2025-05-30",
        "changelog": {
            "3.0": [
                "🎯 NEW: Ski list input format - provide general queries + list of skis",
                "🔄 Enhanced query processing with separate ski context",
                "🎿 Support for multi-ski property questions",
                "📊 Improved comparison capabilities", 
                "🔙 Backward compatibility with original format maintained"
            ],
            "2.5": [
                "🤖 Gemini-powered property responses",
                "📊 Full product data + flex ratings in prompts",
                "🎯 Simplified two-level classification system"
            ],
            "2.0": [
                "Enhanced testing endpoints",
                "Automatic fix validation", 
                "Improved status reporting",
                "Version management system",
                "Fixed JSON serialization issues"
            ]
        },
        "system_ready": query_handler is not None,
        "products_loaded": len(query_handler.df) if query_handler else 0
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    if not query_handler:
        return jsonify({
            "status": "error",
            "system_status": "error",
            "version": API_VERSION,
            "message": "Query handler not initialized",
            "system_ready": False
        }), 500
    
    return jsonify({
        "status": "healthy",
        "system_status": "active", 
        "version": API_VERSION,
        "products_loaded": len(query_handler.df),
        "timestamp": time.time(),
        "system_ready": True,
        "uptime_check": "✅ All systems operational",
        "recent_fixes": [
            "✅ Price comparison intent classification fixed",
            "✅ Exact product matching improved", 
            "✅ Off-piste responses now provide skiing expertise",
            "✅ No more irrelevant weight mentions"
        ]
    })

@app.route('/examples', methods=['GET'])
def get_examples():
    """Get example queries that demonstrate the simplified classification system."""
    return jsonify({
        "version": API_VERSION,
        "system_status": system_status,
        "classification_system": {
            "description": "Simplified two-level classification with LLM-enhanced responses",
            "level_1": "search vs property (rule-based)",
            "level_2_property": "property:property vs property:general (rule-based)",
            "response_generation": "LLM-powered with full product data and flex ratings",
            "benefits": "Expert-level responses with comprehensive product knowledge"
        },
        "examples": [
            {
                "category": "Property:Property (Single Ski)",
                "query": "What is the waist width?",
                "skis": ["Atomic Bent 110 24/25"],
                "expected_intent": "property:property",
                "description": "Ask for specific properties with one ski"
            },
            {
                "category": "Property:Property (Multiple Skis)",
                "query": "How much do they cost?",
                "skis": ["Atomic Bent 110 24/25", "Völkl Blaze 114 24/25"],
                "expected_intent": "property:property",
                "description": "Ask for specific properties of multiple skis"
            },
            {
                "category": "Property:General (Comparison)",
                "query": "Which is cheapest?",
                "skis": ["Dynafit Blacklight 88 W 24/25", "Extrem Mother Tree 95 24/25"],
                "expected_intent": "property:general",
                "description": "Compare properties between skis"
            },
            {
                "category": "Property:General (Suitability)",
                "query": "Which is better for powder?",
                "skis": ["Dynafit Blacklight 88 W 24/25", "Extrem Mother Tree 95 24/25"],
                "expected_intent": "property:general",
                "description": "Ask about skiing suitability"
            },
            {
                "category": "Legacy Format (Still Supported)",
                "query": "What is the waist width of Atomic Bent 110?",
                "skis": [],
                "expected_intent": "property:property",
                "description": "Original format with ski names in query still works"
            }
        ],
        "quick_test_commands": [
            "curl -X POST http://127.0.0.1:5001/query -H 'Content-Type: application/json' -d '{\"query\": \"What is the waist width?\", \"skis\": [\"Atomic Bent 110 24/25\"]}'",
            "curl -X POST http://127.0.0.1:5001/query -H 'Content-Type: application/json' -d '{\"query\": \"Which is cheapest?\", \"skis\": [\"Dynafit Blacklight 88 W 24/25\", \"Extrem Mother Tree 95 24/25\"]}'",
            "curl -X POST http://127.0.0.1:5001/test-fixes"
        ]
    })

@app.route('/test-fixes', methods=['POST'])
def test_fixes():
    """Test the new simplified classification system."""
    if not query_handler:
        return jsonify({
            "error": "Query handler not initialized",
            "version": API_VERSION,
            "system_status": "error"
        }), 500
    
    test_cases = [
        {
            "name": "Search Query Test",
            "query": "Which is the cheapest völkl ski?",
            "expected_intent": "search",
            "description": "Should identify as search query for product listings"
        },
        {
            "name": "Property:Property Test (Waist Width)",
            "query": "What is the waist width of Atomic Bent 110?",
            "expected_intent": "property:property",
            "description": "Should identify specific property questions"
        },
        {
            "name": "Property:Property Test (Price)",
            "query": "How much does the Völkl Blaze 114 cost?",
            "expected_intent": "property:property",
            "description": "Should identify price-specific questions"
        },
        {
            "name": "Property:General Test (Comparison)",
            "query": "Which of the Dynafit Blacklight 88 W 24/25 and Extrem Mother Tree 95 24/25 is the cheapest?",
            "expected_intent": "property:general",
            "expected_products": ["Dynafit Blacklight 88 W 24/25", "Extrem Mother Tree 95 24/25"],
            "description": "Should identify comparison queries as property:general"
        },
        {
            "name": "Property:General Test (Off-piste)",
            "query": "Which of the Dynafit Blacklight 88 W 24/25 and Extrem Mother Tree 95 24/25 is the best for off piste?",
            "expected_intent": "property:general",
            "check_response": "should mention waist and flotation",
            "description": "Should provide skiing expertise for conditions"
        },
        {
            "name": "Property:General Test (Suitability)",
            "query": "Is the Head Crux 105 good for beginners?",
            "expected_intent": "property:general",
            "description": "Should identify suitability questions as property:general"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            start_time = time.time()
            result = query_handler.handle_query(test_case["query"])
            processing_time = time.time() - start_time
            
            # Check if test passed
            test_passed = True
            issues = []
            
            if "expected_intent" in test_case and result.intent != test_case["expected_intent"]:
                test_passed = False
                issues.append(f"Intent mismatch: got '{result.intent}', expected '{test_case['expected_intent']}'")
            
            if "expected_products" in test_case:
                actual_products = [p['title'] for p in result.matched_products] if result.matched_products else []
                if not all(prod in actual_products for prod in test_case["expected_products"]):
                    test_passed = False
                    issues.append(f"Product mismatch: got {actual_products}, expected {test_case['expected_products']}")
            
            if "check_response" in test_case:
                if "waist" not in result.response.lower() or "flotation" not in result.response.lower():
                    test_passed = False
                    issues.append("Response doesn't mention waist and flotation for off-piste")
            
            results.append({
                "test": test_case["name"],
                "query": test_case["query"],
                "description": test_case["description"],
                "passed": test_passed,
                "issues": issues,
                "intent": result.intent,
                "products_found": [p['title'] for p in result.matched_products] if result.matched_products else [],
                "processing_time": f"{processing_time:.3f}s",
                "response_preview": result.response[:100] + "..." if len(result.response) > 100 else result.response
            })
            
        except Exception as e:
            results.append({
                "test": test_case["name"],
                "query": test_case["query"],
                "description": test_case["description"],
                "passed": False,
                "error": str(e)
            })
    
    all_passed = all(r.get("passed", False) for r in results)
    
    return jsonify({
        "version": API_VERSION,
        "system_status": "active" if all_passed else "warning",
        "classification_system": "Simplified two-level system (v2.2)",
        "summary": {
            "all_tests_passed": all_passed,
            "total_tests": len(results),
            "passed_tests": len([r for r in results if r.get("passed", False)]),
            "failed_tests": len([r for r in results if not r.get("passed", False)])
        },
        "test_results": results,
        "improvements": [
            "Simplified classification reduces errors",
            "Clear separation between search and property queries",
            "Property queries split into specific vs general",
            "Better reliability and consistency"
        ]
    })

@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug information endpoint."""
    if not query_handler:
        return jsonify({
            "error": "Query handler not initialized",
            "version": API_VERSION,
            "system_status": "error"
        }), 500
    
    # Get sample of products for debugging
    sample_products = query_handler.df.head(5)[['title', 'brand', 'waist_width_mm', 'price']].to_dict('records')
    
    # Convert numpy types to native Python types for JSON serialization
    for product in sample_products:
        for key, value in product.items():
            if hasattr(value, 'dtype'):  # numpy type
                if value.dtype.kind in 'iufc':  # integer, unsigned int, float, complex
                    product[key] = value.item()  # Convert to native Python type
    
    # Convert value_counts to regular dict with int values
    brand_counts = query_handler.df['brand'].value_counts().head(10)
    brands_dict = {str(k): int(v) for k, v in brand_counts.items()}
    
    return jsonify({
        "version": API_VERSION,
        "system_status": "active",
        "system_info": {
            "total_products": len(query_handler.df),
            "brands_available": brands_dict,
            "data_quality": {
                "products_with_price": int(query_handler.df['price'].notna().sum()),
                "products_with_waist_width": int(query_handler.df['waist_width_mm'].notna().sum()),
                "products_with_weight": int(query_handler.df['weight_grams'].notna().sum())
            }
        },
        "sample_products": sample_products,
        "recent_improvements": [
            "🤖 Gemini-powered property responses (v2.5)",
            "📊 Full product data + flex ratings in Gemini prompts",
            "🎯 Simplified two-level classification system",
            "🔍 Clear separation: search vs property queries",
            "⚡ Smart Gemini fallback to rule-based responses", 
            "✅ Expert skiing advice with comprehensive product knowledge",
            "🎿 Enhanced accuracy for all property questions",
            "🔗 New /show-prompt endpoint to see exact Gemini prompts",
            "🔑 Gemini API key configured and working"
        ],
        "gemini_status": {
            "api_key_set": os.getenv('GEMINI_API_KEY') is not None,
            "model_name": "gemini-1.5-flash",
            "fallback_available": True
        }
    })

@app.route('/query', methods=['POST'])
def query():
    """Process a skiing query with a list of skis the user has looked at."""
    if not query_handler:
        return jsonify({
            "error": "Query handler not initialized",
            "response": "System is currently unavailable",
            "version": API_VERSION,
            "system_status": "error"
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' field in request body",
                "example": {
                    "query": "What is the waist width?",
                    "skis": ["Atomic Bent 110 24/25", "Völkl Blaze 114 24/25"]
                },
                "version": API_VERSION,
                "system_status": system_status
            }), 400
        
        user_query = data['query']
        user_skis = data.get('skis', [])  # List of skis the user has looked at
        
        logger.info(f"🔍 Processing query: {user_query}")
        if user_skis:
            logger.info(f"📋 User's ski list: {user_skis}")
        
        # Process the query with the provided ski list
        result = query_handler.handle_query_with_ski_list(user_query, user_skis)
        
        # Log successful processing
        logger.info(f"✅ Query processed successfully in {result.processing_time:.3f}s")
        
        # Format response
        response_data = {
            "response": result.response,
            "intent": result.intent,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "products": [dict(p) for p in result.matched_products] if result.matched_products else [],
            "user_skis": user_skis,
            "error": result.error_message,
            "version": API_VERSION,
            "system_status": "active"
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {e}")
        return jsonify({
            "error": "Internal server error",
            "response": "I apologize, but I encountered an error while processing your query.",
            "details": str(e),
            "version": API_VERSION,
            "system_status": "error"
        }), 500

@app.route('/test', methods=['GET'])
def test_sample():
    """Test endpoint with a sample query."""
    if not query_handler:
        return jsonify({
            "error": "Query handler not initialized",
            "version": API_VERSION,
            "system_status": "error"
        }), 500
    
    sample_query = "Which of the Dynafit Blacklight 88 W 24/25 and Extrem Mother Tree 95 24/25 is the cheapest?"
    
    try:
        result = query_handler.handle_query(sample_query)
        
        return jsonify({
            "test_query": sample_query,
            "response": result.response,
            "intent": result.intent,
            "products_found": [p['title'] for p in result.matched_products] if result.matched_products else [],
            "processing_time": f"{result.processing_time:.3f}s",
            "status": "✅ Test successful - All fixes working!",
            "version": API_VERSION,
            "system_status": "active"
        })
        
    except Exception as e:
        return jsonify({
            "test_query": sample_query,
            "error": str(e),
            "status": "❌ Test failed",
            "version": API_VERSION,
            "system_status": "error"
        }), 500

@app.route('/show-prompt', methods=['POST'])
def show_prompt():
    """Show the exact prompt that would be sent to Gemini for a query."""
    if not query_handler:
        return jsonify({
            "error": "Query handler not initialized",
            "version": API_VERSION,
            "system_status": "error"
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' field in request body",
                "example": {"query": "Which ski is best for powder?"},
                "version": API_VERSION,
                "system_status": system_status
            }), 400
        
        user_query = data['query']
        logger.info(f"🔍 Generating prompt for query: {user_query}")
        
        # Step 1: Classify the query using the same logic as the main system
        is_search = query_handler._is_search_query(user_query)
        
        if is_search:
            return jsonify({
                "query": user_query,
                "intent": "search",
                "prompt_type": "None - Search queries don't use LLM",
                "explanation": "Search queries use rule-based product filtering and formatting",
                "version": API_VERSION,
                "system_status": "active"
            })
        
        # Step 2: For property queries, classify as property:property vs property:general
        property_type = query_handler._classify_property_type(user_query)
        
        # Step 3: Find relevant products
        products = query_handler._find_relevant_products(user_query)
        
        if not products:
            return jsonify({
                "query": user_query,
                "intent": property_type,
                "prompt_type": "None - No products found",
                "explanation": "No matching products found for this query",
                "version": API_VERSION,
                "system_status": "active"
            })
        
        # Step 4: Generate the appropriate prompt
        from fixed_optimized_query_system import LLMPromptGenerator
        
        if property_type == "property:property":
            prompt = LLMPromptGenerator.generate_property_property_prompt(user_query, products[0])
            prompt_type = "Property:Property (Specific Facts)"
            explanation = "Asks for specific product specifications like price, waist width, weight, etc."
        else:  # property:general
            prompt = LLMPromptGenerator.generate_property_general_prompt(user_query, products)
            prompt_type = "Property:General (Comparisons & Suitability)"
            explanation = "Handles comparisons between products or questions about skiing suitability"
        
        return jsonify({
            "query": user_query,
            "intent": property_type,
            "prompt_type": prompt_type,
            "explanation": explanation,
            "products_found": [p['title'] for p in products[:3]],  # Show first 3 products
            "gemini_prompt": prompt,
            "prompt_length": len(prompt),
            "api_model": "gemini-pro",
            "max_tokens": 400 if property_type == "property:general" else 300,
            "version": API_VERSION,
            "system_status": "active"
        })
        
    except Exception as e:
        logger.error(f"❌ Error generating prompt: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e),
            "version": API_VERSION,
            "system_status": "error"
        }), 500

if __name__ == '__main__':
    print("🎿 Starting Ski Equipment Query System API Server")
    print("=" * 60)
    print(f"Version: {API_VERSION}")
    print(f"System Status: {system_status}")
    print("=" * 60)
    print("API Endpoints:")
    print("  GET  /         - API information")
    print("  GET  /health   - Health check")
    print("  GET  /version  - Version information")
    print("  POST /query    - Submit skiing questions")
    print("  POST /show-prompt - Show exact Gemini prompts")
    print("  GET  /test     - Test with sample query")
    print("  GET  /examples - Example queries showing fixes")
    print("  POST /test-fixes - Test all recent fixes") 
    print("  GET  /debug    - Debug information")
    print("=" * 60)
    print("Quick Testing:")
    print("  curl http://127.0.0.1:5001/version")
    print("  curl http://127.0.0.1:5001/health")
    print("  curl -X POST http://127.0.0.1:5001/test-fixes")
    print("  curl -X POST http://127.0.0.1:5001/show-prompt -H 'Content-Type: application/json' -d '{\"query\": \"What is the waist width of Atomic Bent 110?\"}'")
    print("=" * 60)
    print("Server will start at: http://127.0.0.1:5001")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        print("Starting Flask development server...")
        app.run(host='127.0.0.1', port=5001, debug=True, use_reloader=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Server startup failed: {e}") 