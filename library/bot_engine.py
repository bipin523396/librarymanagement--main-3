import requests
import json
import re
import os

# ----------------- API KEYS & CONFIGURATION ------------------ #
OPENWEATHER_KEY = "9bbb3464a23fbfba4440a2f8a30ebacd"
POLYGON_KEY = "5BFxupg9bm1d3xHsklBgeTOf0yQfPVI"
WIKI_API = "https://en.wikipedia.org/w/api.php"
NEWS_API_KEY = "8bbf59992eec2d04897a5f9a0b93bd9c"
FINNHUB_KEY = "d1ti3mpr01qth6pldro0d1ti3mpr01qth6pldrog"

GOOGLE_API_KEYS = ["AIzaSyDTF68ltRc-3gZBh0qUX2AUNFtbFcm6u7o"]
GOOGLE_CX = "c150745450f7b4d8b"
SEARCHAPI_IO_KEY = "WX2Bu6XFAz3SoXeeuUxSVc4m"
PROXYCRAWL_KEYS = ["Nn15UeXUt8qC5HlaHqpUVA", "UxuA8ZKoxXoK_rqvcGj0Qw"]
SERPAPI_KEY = "09e538a7b57d3f0ad876a3e25dd5dd1ece56236a57dfadf95b86e5bbf3694b40"
ZENSERP_KEY = "456be090-5eb8-11f0-9fdf-59ce8e9d2c54"
SCRAPERAPI_KEYS = ["711e7b8eebd837c04d5f923c254fbebc", "86573e9606d5c94014560c65d25194fa"]

# --- Utility Functions ---
def strip_html(text):
    """Utility to remove html tags and extra whitespace"""
    if not text: return ""
    clean = re.compile('<.*?>')
    cleaned = re.sub(clean, '', text)
    return re.sub(r'\s+', ' ', cleaned).strip()

# --- Search Functions (return multiple snippets for detail) ---
def search_google(query):
    for key in GOOGLE_API_KEYS:
        try:
            res = requests.get("https://www.googleapis.com/customsearch/v1", params={
                "key": key, "cx": GOOGLE_CX, "q": query
            }).json()
            if "items" in res:
                snippets = [item["snippet"] for item in res["items"][:3]]
                return " ".join(snippets)
        except: continue
    return None

def search_searchapiio(query):
    try:
        res = requests.get("https://www.searchapi.io/api/v1/search", params={
            "q": query, "engine": "google", "api_key": SEARCHAPI_IO_KEY
        }).json()
        snippets = [item["snippet"] for item in res.get("organic_results", [])[:3]]
        return " ".join(snippets) if snippets else None
    except: return None

def search_serpapi(query):
    try:
        res = requests.get("https://serpapi.com/search", params={
            "q": query, "api_key": SERPAPI_KEY, "engine": "google"
        }).json()
        snippets = [item["snippet"] for item in res.get("organic_results", [])[:3]]
        return " ".join(snippets) if snippets else None
    except: return None

def search_zenserp(query):
    try:
        res = requests.get("https://app.zenserp.com/api/v2/search", params={
            "q": query, "apikey": ZENSERP_KEY
        }).json()
        snippets = [item["description"] for item in res.get("organic", [])[:3]]
        return " ".join(snippets) if snippets else None
    except: return None

def search_proxycrawl(query):
    for token in PROXYCRAWL_KEYS:
        try:
            res = requests.get("https://api.proxycrawl.com/", params={
                "token": token, "url": f"https://www.google.com/search?q={query}"
            }, verify=False)
            if res.status_code == 200:
                return "Successfully retrieved data via ProxyCrawl."
        except: continue
    return None

def search_scraperapi(query):
    for key in SCRAPERAPI_KEYS:
        try:
            res = requests.get("http://api.scraperapi.com", params={
                "api_key": key, "url": f"https://www.google.com/search?q={query}"
            })
            if res.status_code == 200:
                return "Successfully retrieved data via ScraperAPI."
        except: continue
    return None

def fallback_search(query):
    search_order = [
        search_google, search_searchapiio, search_serpapi,
        search_zenserp, search_proxycrawl, search_scraperapi
    ]
    for func in search_order:
        result = func(query)
        if result:
            return result
    return "No detailed results found."

# --- Live Data APIs ---
def get_weather(city):
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather", params={
            "q": city, "appid": OPENWEATHER_KEY, "units": "metric"
        }).json()
        return f"Weather in {res['name']}: {res['main']['temp']}°C, {res['weather'][0]['description'].capitalize()}."
    except:
        return "Weather data retrieval failed."

def get_polygon_stock(ticker):
    try:
        res = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev", params={
            "adjusted": "true", "apiKey": POLYGON_KEY
        }).json()
        if 'results' in res and res['results']:
            return f"{ticker} Stock: Last Close Price = ${res['results'][0]['c']:.2f}"
        return f"Could not find stock data for ticker {ticker}."
    except:
        return "Stock data retrieval failed."

def get_wiki_summary(topic):
    try:
        res = requests.get(WIKI_API, params={
            "action": "query",
            "prop": "extracts",
            "titles": topic,
            "exintro": True,
            "format": "json"
        }).json()
        page = next(iter(res['query']['pages'].values()))
        if 'extract' in page:
            return strip_html(page['extract'])
        return "No Wikipedia summary found."
    except:
        return "Wikipedia fetch failed."

# --- Image Analysis (Simulated for Now) ---
def analyze_image(image_data=None):
    # This would normally use yolov8 or similar
    # For web integration, we simulate the 'Synergy AI' vision output
    return "Facial detection active: Detected 1 face(s). Expression appears neutral/interested. (Simulated)"

# --- Super AI Engine ---
def super_ai(query, has_image=False):
    if has_image:
        return analyze_image()
        
    query_lower = query.lower()
    
    # 1. Weather check
    if any(word in query_lower for word in ["weather", "temperature", "climate", "forecast", "rain"]):
        # Extract city (last word usually)
        city = query.replace("?", "").split()[-1]
        weather_result = get_weather(city)
        if "failed" not in weather_result.lower():
            return weather_result

    # 2. Finance check
    if any(word in query_lower for word in ["stock", "price", "share", "nifty", "market", "nasdaq", "bse", "sensex"]):
        # Find potential tickers
        for word in query.upper().replace("?", "").split():
            if word.isalpha() and 2 <= len(word) <= 5:
                result = get_polygon_stock(word)
                if "failed" not in result.lower() and "not find" not in result.lower():
                    return result

    # 3. Wikipedia fallback
    wiki_result = get_wiki_summary(query)
    if "failed" not in wiki_result.lower() and "no summary" not in wiki_result.lower():
        # Truncate if too long for chat
        return wiki_result[:500] + "..." if len(wiki_result) > 500 else wiki_result

    # 4. General Web Search fallback
    search_res = fallback_search(query)
    return strip_html(search_res)

