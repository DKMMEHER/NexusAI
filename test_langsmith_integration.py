"""
Test LangSmith Integration Locally (No Auth Version)
This script makes a test image generation request WITHOUT authentication for local testing.
"""

import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = "http://localhost:8001/generate"
TEST_PROMPT = "A beautiful sunset over mountains"
USER_ID = "test_user_langsmith"

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in environment variables!")
    print("   Please set it in your .env file")
    print("   Example: GEMINI_API_KEY=your_key_here")
    exit(1)

print("🧪 Testing LangSmith Integration (Local - No Auth)...\n")
print(f"API URL: {API_URL}")
print(f"Prompt: {TEST_PROMPT}")
print(f"User ID: {USER_ID}\n")

# Make the request with API key (bypasses Firebase auth for local testing)
print("📤 Sending image generation request...")
try:
    response = requests.post(
        API_URL,
        data={
            "prompt": TEST_PROMPT,
            "user_id": USER_ID,
            "model": "gemini-2.5-flash-image",
            "api_key": GEMINI_API_KEY  # Use Gemini API key directly
        },
        timeout=60
    )
    
    print(f"✅ Response Status: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Image generated successfully!")
        print(f"   Job ID: {result.get('job_id', 'N/A')}")
        print(f"   Tokens: {result.get('tokens', 'N/A')}")
        if 'image_url' in result:
            print(f"   Image URL: {result.get('image_url', 'N/A')[:50]}...")
        
        print("\n" + "="*60)
        print("🔍 Now check LangSmith Dashboard:")
        print("="*60)
        print("1. Go to: https://smith.langchain.com/")
        print("2. Select project: NexusAI")
        print("3. Look for trace: 'gemini_image_generation'")
        print(f"4. Filter by metadata.user_id: {USER_ID}")
        print("\nYou should see:")
        print("  ✅ Prompt used")
        print("  ✅ Model called (gemini-2.5-flash-image)")
        print("  ✅ Tokens consumed")
        print("  ✅ Duration")
        print("  ✅ Cost calculated")
        print("="*60)
        
        # Wait a moment for LangSmith to process
        print("\n⏳ Waiting 3 seconds for LangSmith to process trace...")
        time.sleep(3)
        
        # Also test analytics API
        print("\n📊 Testing Analytics API...")
        
        analytics_url = f"http://localhost:8001/analytics/token-usage?user_id={USER_ID}"
        try:
            analytics_response = requests.get(analytics_url, timeout=10)
            
            if analytics_response.status_code == 200:
                analytics_data = analytics_response.json()
                print("✅ Analytics API Response:")
                print(f"   Total Tokens: {analytics_data.get('total_tokens', 0)}")
                print(f"   Total Cost: ${analytics_data.get('total_cost_usd', 0)}")
                print(f"   Operations: {analytics_data.get('operations_count', 0)}")
                
                if analytics_data.get('by_service'):
                    print("\n   By Service:")
                    for service, data in analytics_data.get('by_service', {}).items():
                        print(f"     - {service}: {data.get('tokens', 0)} tokens, ${data.get('cost', 0)}")
            else:
                print(f"⚠️  Analytics API returned: {analytics_response.status_code}")
                print(f"   Response: {analytics_response.text}")
        except Exception as e:
            print(f"⚠️  Analytics API error: {e}")
            
    elif response.status_code == 401:
        print("❌ Authentication error!")
        print("   The service requires authentication.")
        print("   For local testing, make sure you're using api_key parameter.")
        print(f"   Response: {response.text}")
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to the service.")
    print("   Make sure the ImageGeneration service is running:")
    print("   python -m uvicorn ImageGeneration.backend:app --reload --port 8001")
except requests.exceptions.Timeout:
    print("❌ Request timed out (60 seconds)")
    print("   The image generation might be taking longer than expected.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Test complete!")
print("="*60)
print("\n💡 Next Steps:")
print("1. Check LangSmith dashboard: https://smith.langchain.com/")
print("2. Look for project 'NexusAI'")
print("3. Find the trace 'gemini_image_generation'")
print("4. Click on it to see the waterfall view!")
print("\nIf you see the trace, LangSmith integration is working! 🎉")
