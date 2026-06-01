import requests

url = "https://librarymanagement-main-3.vercel.app/"
try:
    response = requests.get(url, timeout=30)
    print(f"Status Code: {response.status_code}")
    if "The God of Small Things" in response.text or "Rich Dad Poor Dad" in response.text:
        print("✅ Home page loaded and books are visible. DB Connection is working for reads.")
    else:
        print("⚠️ Home page loaded but no books found. DB might be empty or connection failed.")
        # Print a bit of the body to see what's there
        print(response.text[:500])
except Exception as e:
    print(f"❌ Failed to reach Vercel: {e}")
