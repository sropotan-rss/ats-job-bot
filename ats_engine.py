from openai import OpenAI
from prompts import build_prompt

client = OpenAI()

def analyze(resume, vacancy):

    prompt = build_prompt(resume, vacancy)

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content
