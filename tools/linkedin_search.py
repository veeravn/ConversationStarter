import os
import requests

def search_linkedin(query: str) -> str:
    params = {
        "q": f"{query} site:linkedin.com/in/",
        "engine": "google",
        "api_key": os.getenv("SERPAPI_API_KEY")
    }
    res = requests.get("https://serpapi.com/search", params=params)
    results = res.json().get("organic_results", [])
    for result in results:
        if "linkedin.com/in/" in result.get("link", ""):
            return result["link"]
    return "No LinkedIn profile found."

