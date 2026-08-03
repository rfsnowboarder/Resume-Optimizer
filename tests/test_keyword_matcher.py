"""
Unit tests for the keyword/skill matching logic.

Run with:  pytest tests/test_keyword_matcher.py
(or just `pytest` from the project root to run all tests)
"""

from src.matching.keyword_matcher import find_skills_in_text, compare_resume_to_jd


def test_find_skills_basic_match():
    text = "I have experience with Python and SQL."
    found = find_skills_in_text(text)
    assert "python" in found
    assert "sql" in found


def test_find_skills_no_false_positive_on_short_words():
    # Regression test: "r" (the R language) should NOT match inside
    # unrelated words like "for" or "experience". This was a real bug
    # caught during development.
    text = "I am looking for a role with growth experience."
    found = find_skills_in_text(text)
    assert "r" not in found


def test_find_skills_case_insensitive():
    text = "Skilled in PYTHON and Sql."
    found = find_skills_in_text(text)
    assert "python" in found
    assert "sql" in found


def test_compare_resume_to_jd_full_match():
    resume = "Experienced with Python and SQL."
    jd = "Looking for someone skilled in Python and SQL."
    result = compare_resume_to_jd(resume, jd)
    assert result["match_score"] == 100
    assert result["missing_skills"] == []


def test_compare_resume_to_jd_partial_match():
    resume = "Experienced with Python."
    jd = "Looking for Python and SQL skills."
    result = compare_resume_to_jd(resume, jd)
    assert "python" in result["matched_skills"]
    assert "sql" in result["missing_skills"]
    assert result["match_score"] == 50


def test_compare_resume_to_jd_no_skills_in_jd():
    resume = "Experienced with Python."
    jd = "This description has no recognizable skill keywords."
    result = compare_resume_to_jd(resume, jd)
    assert result["match_score"] == 0
