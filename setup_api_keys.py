#!/usr/bin/env python3
"""
API Key Setup Script for Qualcomm Linux RAG Q&A Service
"""

import os
import secrets
import getpass

def generate_secure_api_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def setup_api_keys():
    """Interactive setup for API keys"""
    print("🔑 Setting up API Keys for Qualcomm Linux RAG Q&A Service")
    print("=" * 60)
    
    # Generate service API key
    service_api_key = generate_secure_api_key()
    print(f"🔐 Generated Service API Key: {service_api_key}")
    print()
    
    # Get Gemini API key
    print("🌐 Google Gemini API Key Setup:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated key")
    print()
    
    # gemini_key = getpass.getpass("Enter your Gemini API key (will be hidden): ")
    gemini_key = "AIzaSyAVBDGK6lP9SjFuAG0c3VxJ3Jly25LUBy0"
    if not gemini_key or gemini_key.strip() == "":
        print("❌ No Gemini API key provided. LLM functionality will be limited.")
        gemini_key = "test_gemini_key"
    
    # Create environment variables
    env_content = f"""# API Keys for Qualcomm Linux RAG Q&A Service
# Generated on: {os.popen('date').read().strip()}

# Service API Key (for accessing the RAG service)
API_KEY={service_api_key}

# Google Gemini API Key (for LLM functionality)
GEMINI_API_KEY={gemini_key}

# Environment settings
ENVIRONMENT=production
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ API Keys configured successfully!")
    print(f"📁 Configuration saved to: .env")
    print()
    print("🚀 To start the service with these keys:")
    print(f"docker run -d --name hkthon-prod \\")
    print(f"  -e API_KEY={service_api_key} \\")
    print(f"  -e GEMINI_API_KEY={gemini_key} \\")
    print(f"  -p 8000:8000 hkthon-rag")
    print()
    print("🔒 Keep your API keys secure and don't share them!")
    
    return service_api_key, gemini_key

if __name__ == "__main__":
    setup_api_keys() 