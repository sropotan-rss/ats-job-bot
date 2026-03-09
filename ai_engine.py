import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze(resume, vacancy):

    prompt = f"""
Ты HR эксперт.

Проанализируй резюме и вакансию.

Ответь в формате:

ATS ОЦЕНКА (0-100)

СИЛЬНЫЕ СТОРОНЫ
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

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return completion.choices[0].message.content
