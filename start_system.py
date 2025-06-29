#!/usr/bin/env python3
"""
Startup Script for Ski Equipment Query System
Launches both Flask API server and Streamlit frontend
"""

import subprocess
import sys
import time
import requests
import webbrowser

def check_api_health():
    """Check if Flask API is running."""
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("🎿 Starting Ski Equipment Query System")
    print("=" * 50)
    
    # Check if Flask API is already running
    if check_api_health():
        print("✅ Flask API server already running at http://127.0.0.1:5000")
    else:
        print("🚀 Starting Flask API server...")
        try:
            # Start Flask API in background
            subprocess.Popen([sys.executable, "api_server.py"])
            
            # Wait for API to start
            for i in range(10):
                time.sleep(1)
                if check_api_health():
                    print("✅ Flask API server started successfully!")
                    break
                print(f"   Waiting for API... ({i+1}/10)")
            else:
                print("❌ Failed to start Flask API server")
                return
        except Exception as e:
            print(f"❌ Error starting Flask API: {e}")
            return
    
    print("🎨 Starting Streamlit frontend...")
    print("=" * 50)
    print("📱 Frontend will open at: http://localhost:8501")
    print("🔧 API running at: http://127.0.0.1:5000")
    print("=" * 50)
    print("Press Ctrl+C to stop both servers")
    print("=" * 50)
    
    try:
        # Start Streamlit frontend
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend.py"])
    except KeyboardInterrupt:
        print("\n🛑 Shutting down system...")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

if __name__ == "__main__":
    main() 