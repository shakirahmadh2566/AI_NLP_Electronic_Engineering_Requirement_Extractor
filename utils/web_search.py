import requests
from bs4 import BeautifulSoup

def web_search(query):
    url = f"https://duckduckgo.com/html/?q={query}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    for a in soup.find_all("a", class_="result__a")[:5]:
        results.append(a.get_text())

    return results