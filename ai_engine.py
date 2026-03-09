import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama3-8b-8192"


def analyze_resume_vacancy(resume, vacancy):

    resume = resume[:1500]
    vacancy = vacancy[:1500]

    prompt = f"""
Ты HR эксперт.

Оцени насколько кандидат подходит под вакансию.

Ответь кратко:

ATS SCORE (0-100)

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
        max_tokens=300
    )

    return completion.choices[0].message.content
