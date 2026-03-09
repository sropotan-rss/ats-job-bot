import requests
from bs4 import BeautifulSoup

def parse_vacancy(url):

    try:

        r = requests.get(url, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        text = soup.get_text()

        return text[:4000]

    except:
        return url
