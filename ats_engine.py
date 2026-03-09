import os
import requests

API_KEY = os.getenv("HF_API_KEY")

API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def analyze(resume, vacancy):

    prompt = f"""
Ты HR эксперт.

Проанализируй резюме и вакансию.

Ответь на русском языке.

Формат ответа:

ATS ОЦЕНКА (0-100)

ПОДХОДЯЩИЕ НАВЫКИ
- ...

ЧЕГО НЕ ХВАТАЕТ
- ...

СОВЕТЫ
- ...

Резюме:
{resume}

Вакансия:
{vacancy}
"""

    data = {
        "inputs": prompt
    }

    response = requests.post(API_URL, headers=headers, json=data)

    result = response.json()

    if isinstance(result, list):
        return result[0]["generated_text"]

    return str(result)
