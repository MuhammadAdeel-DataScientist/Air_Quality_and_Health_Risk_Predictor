"""
Debug script to verify .env file is loaded correctly
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Test 1: Check if .env exists
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

print("="*60)
print("ENVIRONMENT VARIABLE DEBUG")
print("="*60)

print(f"\n1. Current working directory: {os.getcwd()}")
print(f"2. Script location: {BASE_DIR}")
print(f"3. Expected .env path: {ENV_PATH}")
print(f"4. .env file exists: {ENV_PATH.exists()}")

if ENV_PATH.exists():
    print(f"5. .env file size: {ENV_PATH.stat().st_size} bytes")
    
    # Load .env
    load_dotenv(dotenv_path=ENV_PATH)
    
    print("\n" + "="*60)
    print("API KEYS STATUS")
    print("="*60)
    
    # Test each API key
    api_keys = {
        "OPENWEATHER_API_KEY": os.getenv("OPENWEATHER_API_KEY"),
        "IQAIR_API_KEY": os.getenv("IQAIR_API_KEY"),
        "WAQI_API_KEY": os.getenv("WAQI_API_KEY"),
        "OPENAQ_API_KEY": os.getenv("OPENAQ_API_KEY")
    }
    
    for key_name, key_value in api_keys.items():
        if key_value:
            # Show first 10 and last 4 characters for security
            masked = f"{key_value[:10]}...{key_value[-4:]}"
            print(f"✓ {key_name}: {masked}")
        else:
            print(f"✗ {key_name}: NOT FOUND")
    
    # Check from Config class
    print("\n" + "="*60)
    print("CONFIG CLASS CHECK")
    print("="*60)
    
    try:
        from src.config.config import Config
        
        if Config.api.OPENAQ_API_KEY:
            masked = f"{Config.api.OPENAQ_API_KEY[:10]}...{Config.api.OPENAQ_API_KEY[-4:]}"
            print(f"✓ Config.api.OPENAQ_API_KEY: {masked}")
        else:
            print(f"✗ Config.api.OPENAQ_API_KEY: None or Empty")
            
    except Exception as e:
        print(f"✗ Error loading Config: {e}")

else:
    print("\n❌ .env file NOT FOUND!")
    print("\nPlease ensure .env file exists in the project root directory")
    print(f"Expected location: {ENV_PATH}")

print("\n" + "="*60)