# tools/web_search.py
import urllib.parse
import webbrowser
import requests

def search_web(query: str) -> str:
    """
    Searches the web for a query and opens the search results in the browser.
    :param query: Search term or question.
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    webbrowser.open(url)
    return f"I've opened the web search results for '{query}' in your browser."

def fetch_quick_answer(query: str) -> str:
    """
    Fetches quick summary information from DuckDuckGo API for factual queries.
    :param query: Topic or search keyword.
    """
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json"
        response = requests.get(url, timeout=5).json()
        abstract = response.get("AbstractText", "")
        if abstract:
            return f"Summary for '{query}': {abstract}"
        return f"No quick summary found for '{query}'. Try search_web instead."
    except Exception as e:
        return f"Failed to fetch quick answer: {str(e)}"