"""
Handles calling the Claude API to generate resume feedback and
tailored rewrite suggestions.

This is where the AI-powered part of the app lives — everything before
this (parsing, keyword matching) was deterministic code. This module
sends the resume + job description to Claude and asks it to reason
about fit and suggest improvements, which is something plain keyword
matching can't do (e.g. judging whether experience depth matches what
the JD is asking for).
"""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

# Load variables from the .env file (ANTHROPIC_API_KEY) into the environment
load_dotenv(encoding="utf-8-sig")

MODEL = "claude-sonnet-4-6"

# This system prompt sets the AI's guardrails and "voice." Keeping this in
# one place makes it easy to iterate on without touching the rest of the code.
SYSTEM_PROMPT = """You are a resume coach helping a job seeker tailor their \
resume to a specific job description.

Rules you must always follow:
- NEVER invent achievements, metrics, job titles, or experience the \
resume doesn't already contain. Only rephrase or reorganize what is \
truthfully there.
- If the resume is missing something the job description asks for, say \
so plainly rather than fabricating it.
- Be specific and actionable, not generic ("use stronger verbs" is not \
useful; show the actual rewritten line).
- Keep a supportive, direct tone — this person is likely stressed about \
their job search. Be encouraging but honest.

Your response should include:
1. A brief assessment of whether the resume's experience LEVEL and DEPTH \
genuinely matches what the job description is asking for (not just \
whether keywords are present).
2. 3-5 specific bullet point rewrites from the resume, tailored to better \
match the job description's language and priorities.
3. Any honest gaps the person should be aware of, stated kindly but clearly.
"""


def get_ai_feedback(resume_text: str, jd_text: str) -> str:
    """
    Sends the resume and job description to Claude and returns
    the AI's feedback as a string.

    Raises a RuntimeError with a friendly message if the API key
    is missing or the call fails, so the Streamlit app can display
    something useful instead of a raw crash.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No API key found. Make sure your .env file exists and contains "
            "ANTHROPIC_API_KEY=your_key_here."
        )

    client = Anthropic(api_key=api_key)

    user_message = f"""Here is my resume:

{resume_text}

Here is the job description I'm applying to:

{jd_text}

Please give me feedback and rewrite suggestions as described in your \
instructions."""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as e:
        raise RuntimeError(f"Claude API call failed: {e}")

    # response.content is a list of content blocks; we just want the text
    return "".join(block.text for block in response.content if block.type == "text")
