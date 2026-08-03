"""
Unit tests for the ATS formatting rule checks.

Run with:  pytest tests/test_ats_check.py
"""

from src.ats_check.formatting_rules import (
    check_contact_info,
    check_standard_sections,
    run_ats_checks,
)


def test_check_contact_info_detects_email_and_phone():
    text = "Reach me at jane.doe@email.com or (555) 123-4567."
    result = check_contact_info(text)
    assert result["has_email"] is True
    assert result["has_phone"] is True


def test_check_contact_info_missing_both():
    text = "No contact details here at all."
    result = check_contact_info(text)
    assert result["has_email"] is False
    assert result["has_phone"] is False


def test_check_standard_sections_all_present():
    text = "Experience\nWorked at a company.\n\nEducation\nWent to school.\n\nSkills\nPython, SQL."
    result = check_standard_sections(text)
    assert result["experience"] is True
    assert result["education"] is True
    assert result["skills"] is True


def test_run_ats_checks_clean_resume_has_no_issues():
    clean_resume = """Jane Doe
jane.doe@email.com | (555) 123-4567

Experience
Data Analyst at Acme Corp

Education
BS in Statistics

Skills
Python, SQL
"""
    report = run_ats_checks(clean_resume)
    assert report["issues"] == []


def test_run_ats_checks_flags_missing_contact_and_sections():
    bad_resume = "Just some random text with no structure."
    report = run_ats_checks(bad_resume)
    assert len(report["issues"]) > 0
    assert any("email" in issue.lower() for issue in report["issues"])
