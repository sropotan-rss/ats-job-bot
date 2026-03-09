def build_prompt(resume, vacancy):

    return f"""
You are an ATS system.

Analyze resume vs vacancy.

Tasks:

1 Calculate ATS match score
2 Find missing keywords
3 Suggest keywords to ADD
4 Generate cover letter

Resume:
{resume}

Vacancy:
{vacancy}

Return format:

ATS MATCH:

MISSING KEYWORDS:

WHAT TO ADD:

COVER LETTER:
"""
