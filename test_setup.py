#!/usr/bin/env python3
"""
Test script to verify API keys and basic connectivity
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_api():
    """Test Groq API connectivity"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ GROQ_API_KEY not found in .env file"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "messages": [{"role": "user", "content": "Say 'Hello SwarmBot!'"}],
        "model": "llama-3.2-90b-vision-preview",
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return f"✅ Groq API working! Response: {content}"
        else:
            return f"❌ Groq API error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Groq API connection failed: {str(e)}"

def test_env_setup():
    """Test environment setup"""
    print("🔍 Testing Environment Setup")
    print("=" * 60)
    
    # Check Python version
    import sys
    print(f"Python version: {sys.version}")
    
    # Check environment variables
    env_vars = ["GROQ_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Found (length: {len(value)} chars)")
        else:
            print(f"❌ {var}: Not found")
    
    print("\n🔍 Testing API Connectivity")
    print("=" * 60)
    print(test_groq_api())

if __name__ == "__main__":
    test_env_setup()
