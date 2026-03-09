import requests
from bs4 import BeautifulSoup

def parse_vacancy(url_or_text: str) -> str:

    if url_or_text.startswith("http"):
        try:
            r = requests.get(url_or_text, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text()
            return text[:4000]
        except:
            return url_or_text

    return url_or_text
