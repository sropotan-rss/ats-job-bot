import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze(resume, vacancy):

    prompt = f"""

You are an ATS system.

Resume:
{resume}

Vacancy:
{vacancy}

Return:

1 ATS SCORE (0-100)

2 Missing keywords

3 What to ADD to resume (do not rewrite resume)

4 Short cover letter

"""

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[
            {"role": "user", "content": prompt}
        ]

    )

    return response.choices[0].message.content
