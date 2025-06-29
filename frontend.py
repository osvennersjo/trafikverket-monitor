#!/usr/bin/env python3
"""
Streamlit Frontend for Ski Equipment Query System
Version 2.1 - Enhanced Status and Version Display
Beautiful web interface for asking skiing questions powered by our Flask API.
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="🎿 Ski Equipment Query System",
    page_icon="🎿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .query-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .response-box {
        background: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .metrics-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .status-active {
        background: #d4edda;
        border-left-color: #28a745;
    }
    .status-error {
        background: #f8d7da;
        border-left-color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://127.0.0.1:5001"

def get_api_version():
    """Get version information from the Flask API."""
    try:
        response = requests.get(f"{API_BASE_URL}/version", timeout=2)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"API returned status {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def check_api_health():
    """Check if the Flask API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, {"error": f"API returned status {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def send_query(query_text, ski_list=None):
    """Send query to the Flask API with optional ski list."""
    try:
        start_time = time.time()
        
        # Prepare request data
        request_data = {"query": query_text}
        if ski_list:
            request_data["skis"] = ski_list
        
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=request_data,
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            data['frontend_time'] = end_time - start_time
            return True, data
        else:
            return False, {"error": f"API error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": f"Connection error: {str(e)}"}

# Main UI
def main():
    # Header
    st.markdown('<h1 class="main-header">🎿 Ski Equipment Query System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ask any question about ski equipment and get expert recommendations powered by AI!</p>', unsafe_allow_html=True)
    
    # Get version and health information
    version_success, version_data = get_api_version()
    api_healthy, health_data = check_api_health()
    
    if not api_healthy:
        st.markdown(f"""
        <div class="error-box">
            <h3>⚠️ API Server Not Available</h3>
            <p>The Flask API server is not running. Please start it by running:</p>
            <code>python3 api_server.py</code>
            <p><strong>Error:</strong> {health_data.get('error', 'Unknown error')}</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display version and status information
    status = health_data.get('status', 'unknown')
    status_class = 'status-active' if status == 'active' else 'status-error'
    
    # Create columns for version and status
    col1, col2 = st.columns(2)
    
    with col1:
        if version_success:
            version_info = version_data.get('version', 'Unknown')
            st.markdown(f"""
            <div class="metrics-box status-active">
                <h4>📦 System Version: {version_info}</h4>
                <p>Frontend: v2.1 | Backend: v{version_info}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metrics-box status-error">
                <h4>📦 Version: Unknown</h4>
                <p>Could not retrieve version information</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        products_count = health_data.get('products_loaded', 0)
        st.markdown(f"""
        <div class="metrics-box {status_class}">
            <h4>🟢 Status: {status.title()}</h4>
            <p>📊 Products loaded: <strong>{products_count}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # New input format explanation
    st.markdown("### 🎯 New Query Format:")
    st.info("**Ask general questions** (like 'What is the waist width?' or 'Which is better for powder?') and **provide a list of skis** you've been looking at below.")
    
    # Example queries for the new format
    st.markdown("### 💡 Try these example questions:")
    example_cols = st.columns(3)
    
    examples = [
        "What is the waist width?",
        "Which is cheapest?", 
        "Which is better for powder?",
        "How much do they cost?",
        "Which is lightest?",
        "Which is best for beginners?"
    ]
    
    for i, example in enumerate(examples):
        col = example_cols[i % 3]
        if col.button(f"🎯 {example}", key=f"example_{i}"):
            st.session_state.query_input = example
    
    # Query input
    st.markdown("### 🗣️ Ask your skiing question:")
    
    # Initialize session state
    if 'query_input' not in st.session_state:
        st.session_state.query_input = ""
    if 'ski_list' not in st.session_state:
        st.session_state.ski_list = []
    
    query = st.text_input(
        "Enter your general question:",
        value=st.session_state.query_input,
        placeholder="e.g., What is the waist width? or Which is better for powder?",
        help="Ask general questions without mentioning specific ski names!"
    )
    
    # Ski list input
    st.markdown("### 🎿 Skis you're considering:")
    
    # Add ski input
    col1, col2 = st.columns([3, 1])
    with col1:
        new_ski = st.text_input(
            "Add a ski to compare:",
            placeholder="e.g., Atomic Bent 110 24/25",
            help="Type the full ski name including year (e.g., 24/25)"
        )
    with col2:
        if st.button("➕ Add Ski"):
            if new_ski.strip() and new_ski.strip() not in st.session_state.ski_list:
                st.session_state.ski_list.append(new_ski.strip())
                st.rerun()
    
    # Display current ski list
    if st.session_state.ski_list:
        st.markdown("**Current ski list:**")
        for i, ski in enumerate(st.session_state.ski_list):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"🎿 {ski}")
            with col2:
                if st.button("🗑️", key=f"remove_{i}"):
                    st.session_state.ski_list.pop(i)
                    st.rerun()
    else:
        st.info("Add some skis above to compare them!")
    
    # Query submission
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        submit_button = st.button("🔍 Ask Question", type="primary", use_container_width=True)
    
    # Process query
    if submit_button and query.strip():
        if not st.session_state.ski_list:
            st.warning("⚠️ Please add at least one ski to your list before asking a question!")
        else:
            with st.spinner("🤔 Thinking... Getting expert skiing advice..."):
                success, result = send_query(query.strip(), st.session_state.ski_list)
            
            if success:
                # Display query and ski list
                st.markdown(f"""
                <div class="query-box">
                    <h4>📝 Your Question:</h4>
                    <p><em>"{query}"</em></p>
                    <h4>🎿 About these skis:</h4>
                    <p>{', '.join(st.session_state.ski_list)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display response
                st.markdown(f"""
                <div class="response-box">
                    <h4>🎿 Expert Answer:</h4>
                    <p>{result.get('response', 'No response received')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Intent", result.get('intent', 'unknown').title())
                
                with col2:
                    confidence = result.get('confidence', 0)
                    st.metric("Confidence", f"{confidence:.0%}")
                
                with col3:
                    processing_time = result.get('processing_time', 0) * 1000
                    st.metric("Processing Time", f"{processing_time:.0f}ms")
                
                with col4:
                    products_found = len(result.get('products', []))
                    st.metric("Products Found", products_found)
                
                # Display matched products
                products = result.get('products', [])
                if products:
                    st.markdown("### 🎯 Matched Products:")
                    
                    for i, product in enumerate(products, 1):
                        with st.expander(f"🎿 {i}. {product.get('title', 'Unknown Product')} (Score: {product.get('match_score', 0):.2f})"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Waist Width:** {product.get('waist_width_mm', 'N/A')}mm")
                                st.write(f"**Price:** {product.get('price', 'N/A')} SEK")
                                
                            with col2:
                                lengths = product.get('parsed_lengths', [])
                                if lengths:
                                    st.write(f"**Available Lengths:** {', '.join(map(str, lengths))}cm")
                                else:
                                    st.write("**Available Lengths:** Not specified")
                                
                                weight = product.get('weight_grams')
                                if weight and not pd.isna(weight):
                                    st.write(f"**Weight:** {weight}g")
                                else:
                                    st.write("**Weight:** Not available")
                
                # Error handling
                if result.get('error'):
                    st.markdown(f"""
                    <div class="error-box">
                        <h4>⚠️ Note:</h4>
                        <p>{result.get('error')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            else:
                st.markdown(f"""
                <div class="error-box">
                    <h4>❌ Error Processing Query</h4>
                    <p>{result.get('error', 'Unknown error occurred')}</p>
                    <p>Please check that the Flask API server is running and try again.</p>
                </div>
                """, unsafe_allow_html=True)
    
    elif submit_button and not query.strip():
        st.warning("⚠️ Please enter a question before submitting!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎿 Powered by advanced AI and comprehensive ski equipment database</p>
        <p>Built with Streamlit + Flask + Python | Data integrity guaranteed ✅</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 