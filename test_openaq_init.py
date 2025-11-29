"""
Quick test to verify OpenAQ client initialization
"""
from src.config.config import Config
from src.data_pipeline.api_clients import OpenAQClient

print("="*60)
print("OPENAQ CLIENT INITIALIZATION TEST")
print("="*60)

# Check config
print(f"\n1. Config.api.OPENAQ_API_KEY exists: {hasattr(Config.api, 'OPENAQ_API_KEY')}")

if hasattr(Config.api, 'OPENAQ_API_KEY'):
    key = Config.api.OPENAQ_API_KEY
    if key:
        print(f"2. API Key loaded: {key[:10]}...{key[-4:]}")
    else:
        print("2. API Key is None or empty")
else:
    print("2. OPENAQ_API_KEY attribute not found in Config")

# Initialize client
print("\n3. Initializing OpenAQClient...")
try:
    client = OpenAQClient()
    
    if client.api_key:
        print(f"   ✓ Client initialized with key: {client.api_key[:10]}...{client.api_key[-4:]}")
    else:
        print("   ✗ Client initialized but api_key is None")
    
    # Check if _get_headers method exists
    if hasattr(client, '_get_headers'):
        headers = client._get_headers()
        print(f"   ✓ _get_headers() method exists")
        print(f"   Headers: {headers}")
    else:
        print("   ✗ _get_headers() method NOT FOUND")
        print("   You need to update the OpenAQClient class!")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*60)