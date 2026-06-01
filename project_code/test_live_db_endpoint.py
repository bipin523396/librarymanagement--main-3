import requests

url = "https://librarymanagement-main-3.vercel.app/en/library/test-db/"
try:
    response = requests.get(url, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Failed to reach Vercel test-db: {e}")
