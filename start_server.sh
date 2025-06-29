#!/bin/bash
export GEMINI_API_KEY="AIzaSyAOYbQD5dAAQsYyK4lfFp-ciiXJgj3prCw"
echo "Starting Flask server with Gemini API key..."
echo "API Key status: $([[ -n "$GEMINI_API_KEY" ]] && echo "SET" || echo "NOT SET")"
python3 api_server.py 