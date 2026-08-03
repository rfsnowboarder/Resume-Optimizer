"""
Compares resume text against job description text and reports which
skills (from our reference list) appear in each, plus a simple
match score.

This is intentionally simple string matching for Phase 1 — no AI
involved. It's fast, free, and easy to understand/debug, which makes
it a good foundation before we add smarter (AI-powered) matching later.
"""

import re

from src.matching.skills_list import COMMON_SKILLS


def find_skills_in_text(text: str) -> set:
    """
    Returns the set of skills (from COMMON_SKILLS) that appear
    anywhere in the given text. Case-insensitive.

    Uses word-boundary matching (not plain substring search) so that
    short skills like "r" don't false-positive match inside unrelated
    words such as "for" or "experience". Skills containing symbols
    (like "a/b testing" or "c++") still match correctly since we only
    require a boundary, not that neighboring characters be letters.
    """
    text_lower = text.lower()
    found = set()
    for skill in COMMON_SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def compare_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    """
    Compares the resume and job description and returns:
      - matched_skills: skills found in both
      - missing_skills: skills the JD wants but the resume doesn't mention
      - extra_skills: skills the resume has that the JD doesn't mention
      - match_score: percentage of JD-requested skills that the resume covers
    """
    resume_skills = find_skills_in_text(resume_text)
    jd_skills = find_skills_in_text(jd_text)

    matched_skills = resume_skills & jd_skills          # in both
    missing_skills = jd_skills - resume_skills           # JD wants, resume lacks
    extra_skills = resume_skills - jd_skills              # resume has, JD didn't ask

    if jd_skills:
        match_score = round(len(matched_skills) / len(jd_skills) * 100)
    else:
        match_score = 0  # no recognizable skills found in the JD at all

    return {
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "extra_skills": sorted(extra_skills),
        "match_score": match_score,
    }
