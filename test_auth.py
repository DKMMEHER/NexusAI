import requests

SERVICES = {
    "Director": "http://localhost:8006/my_jobs/test_user",
    "ImageGeneration": "http://localhost:8000/image/my_images/test_user", 
    "Documents": "http://localhost:8003/analytics?user_id=test_user",
    "YouTube": "http://localhost:8004/analytics?user_id=test_user",
    "Chat": "http://localhost:8005/analytics?user_id=test_user"
}

def test_unauthorized_access():
    print("Testing Unauthorized Access (expecting 403/401)...")
    for name, url in SERVICES.items():
        try:
            # We provide a fake token or no token
            headers = {"Authorization": "Bearer invalid_token"} 
            # Note: For dependencies check logic, verify_token might raise 401 if invalid,
            # or 403 if valid token but uid mismatch.
            # Here we act as if we are sending a request without a valid token.
            
            res = requests.get(url, headers=headers)
            print(f"[{name}] Status: {res.status_code}")
            if res.status_code == 200:
                print(f"[{name}] Body: {res.text[:100]}...")
            
            if res.status_code in [401, 403]:
                print(f"✅ {name} secured.")
            else:
                print(f"❌ {name} failed security check. Got {res.status_code}")
                
        except Exception as e:
            print(f"⚠️ {name} connection failed: {e}")

if __name__ == "__main__":
    test_unauthorized_access()
