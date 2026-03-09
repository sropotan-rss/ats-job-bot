import requests


def search_jobs(query):

    url = "https://api.hh.ru/vacancies"

    params = {
        "text": query,
        "per_page": 10
    }

    r = requests.get(url, params=params, timeout=20)

    data = r.json()

    links = []

    for item in data.get("items", []):

        links.append(item["alternate_url"])

    return links
