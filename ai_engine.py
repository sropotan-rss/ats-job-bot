import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama3-8b-8192"


def analyze(resume: str, vacancy: str) -> str:

    # Ограничиваем текст чтобы ускорить AI
    resume = resume[:2000]
    vacancy = vacancy[:2000]

    prompt = f"""
Ты HR эксперт.

Сравни резюме и вакансию.

Ответь коротко:

ATS ОЦЕНКА (0-100)

СИЛЬНЫЕ СТОРОНЫ
- ...

ЧЕГО НЕ ХВАТАЕТ
- ...

Резюме:
{resume}

Вакансия:
{vacancy}
"""

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=400
    )

    return completion.choices[0].message.content
