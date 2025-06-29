#!/usr/bin/env python3
"""
Test runner for the optimized query system
"""

import subprocess
import sys
import os

def run_test():
    """Run the optimized query system test."""
    try:
        print("🚀 Starting Optimized Query System Test...")
        print("=" * 60)
        
        # Check if the optimized system file exists
        if not os.path.exists('optimized_query_system.py'):
            print("❌ optimized_query_system.py not found!")
            return False
        
        # Check if the data file exists
        if not os.path.exists('alpingaraget_ai_optimized.csv'):
            print("❌ alpingaraget_ai_optimized.csv not found!")
            return False
        
        # Run the optimized system
        result = subprocess.run([sys.executable, 'optimized_query_system.py'], 
                              capture_output=True, text=True, timeout=60)
        
        print("📊 TEST RESULTS:")
        print("=" * 60)
        
        if result.returncode == 0:
            print("✅ Test completed successfully!")
            print("\n📋 OUTPUT:")
            print(result.stdout)
        else:
            print("❌ Test failed!")
            print("\n🔍 ERROR OUTPUT:")
            print(result.stderr)
            print("\n📋 STDOUT:")
            print(result.stdout)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1) 