import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze(resume, vacancy):

    try:

        prompt = f"""
Проанализируй резюме и вакансию.

Ответь на русском.

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

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"Ошибка AI анализа:\n{str(e)}"
