"""
Rule-based checks for common resume formatting issues that trip up
real-world ATS (Applicant Tracking System) parsers.

Important honesty note: we only have access to the TEXT that was
extracted from the resume file, not its original visual layout. So we
can't directly detect things like "this resume uses a 2-column layout"
or "this uses a text box." Instead, we look for *symptoms* of those
problems in how the extracted text comes out — e.g. garbled or
run-together text is a strong sign the original file used a layout
that a real ATS would also struggle with.

This is intentionally simple, deterministic, rule-based code — no AI
involved, which keeps it fast, free, and easy to reason about.
"""

import re

EXPECTED_SECTIONS = [
    "experience", "education", "skills",
]

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")


def check_contact_info(text: str) -> dict:
    """Checks whether an email and phone number are detectable in the text."""
    has_email = bool(EMAIL_PATTERN.search(text))
    has_phone = bool(PHONE_PATTERN.search(text))
    return {"has_email": has_email, "has_phone": has_phone}


def check_standard_sections(text: str) -> dict:
    """
    Checks whether common resume section headers are present.
    Real ATS systems rely heavily on recognizing these headers to
    correctly categorize your resume's content.
    """
    text_lower = text.lower()
    found = {section: section in text_lower for section in EXPECTED_SECTIONS}
    return found

def check_text_quality(text: str) -> dict:
    """
    Looks for signs that the original file layout confused the text
    extractor — a strong proxy for "a real ATS would struggle with this
    too," since ATS parsers use similar underlying extraction methods.
    """
    lines = [line for line in text.split("\n") if line.strip()]

    if not lines:
        return {"issue": "No readable text was found at all — likely a scanned or image-based file."}

    avg_line_length = sum(len(line) for line in lines) / len(lines)

    # Suspiciously long lines can indicate multi-column layouts that got
    # merged together by the extractor (a known ATS pain point).
    long_line_flag = avg_line_length > 200

    # A resume with very few line breaks relative to its length can
    # indicate text boxes or tables that extracted as one big blob.
    very_few_lines = len(lines) < 5 and len(text) > 500

    return {
        "avg_line_length": round(avg_line_length),
        "possible_column_layout": long_line_flag,
        "possible_table_or_textbox": very_few_lines,
    }


def run_ats_checks(resume_text: str) -> dict:
    """
    Runs all ATS checks and returns a combined report along with a
    plain-language list of issues found (if any).
    """
    contact = check_contact_info(resume_text)
    sections = check_standard_sections(resume_text)
    quality = check_text_quality(resume_text)

    issues = []

    if not contact["has_email"]:
        issues.append("No email address detected — make sure it's typed as plain text, not an image or icon.")
    if not contact["has_phone"]:
        issues.append("No phone number detected — same advice, avoid embedding it in an image/graphic.")

    for section, found in sections.items():
        if not found:
            issues.append(f"No clear '{section.title()}' section header found. ATS systems often rely on standard headers to categorize content.")

    if quality.get("possible_column_layout"):
        issues.append("Text extraction produced unusually long lines — this often happens with multi-column layouts, which many ATS systems parse incorrectly.")

    if quality.get("possible_table_or_textbox"):
        issues.append("Very little text was extracted relative to file size — this can indicate content is inside tables, text boxes, or images, which many ATS systems can't read at all.")

    if quality.get("issue"):
        issues.append(quality["issue"])

    return {
        "contact": contact,
        "sections": sections,
        "quality": quality,
        "issues": issues,
    }
