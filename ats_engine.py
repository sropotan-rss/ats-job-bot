import os
import requests

API_KEY = os.getenv("HF_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}


def analyze(resume, vacancy):

    prompt = f"""
Ты HR эксперт.

Проанализируй резюме и вакансию.

Ответь на русском языке.

Формат:

ATS ОЦЕНКА (0-100)

ПОДХОДЯЩИЕ НАВЫКИ
...

ЧЕГО НЕ ХВАТАЕТ
...

СОВЕТЫ
...

Резюме:
{resume}

Вакансия:
{vacancy}
"""

    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": prompt}
    )

    result = response.json()

    return str(result)
