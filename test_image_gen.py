import requests
import os

# Ensure no API key is set in env for this test to trigger 401
if "GEMINI_API_KEY" in os.environ:
    del os.environ["GEMINI_API_KEY"]

url = "http://127.0.0.1:8000/image/generate"
data = {
    "prompt": "test prompt",
    "model": "gemini-2.5-flash-image"
}

try:
    print(f"Sending request to {url} without API key...")
    # Do not pass api_key in data
    response = requests.post(url, data=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 500 and "401" in response.text:
        print("\nSUCCESS: Reproduction confirmed. Wrapper caught 401 and returned 500.")
    elif response.status_code == 401:
        print("\nFAILURE: Could not reproduce. Server returned correct 401.")
    else:
        print(f"\nUNKNOWN: Server returned {response.status_code}")

except Exception as e:
    print(f"Script Error: {e}")
