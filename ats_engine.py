import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze(resume, vacancy):

    prompt = f"""
Ты профессиональная ATS система HR.

Проанализируй резюме и вакансию.

Ответь на русском языке в формате:

ATS ОЦЕНКА: (0-100)

ПОДХОДЯЩИЕ НАВЫКИ
- ...

ОТСУТСТВУЮЩИЕ НАВЫКИ
- ...

СОВЕТЫ КАК УЛУЧШИТЬ РЕЗЮМЕ
- ...

Резюме:
{resume}

Вакансия:
{vacancy}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
