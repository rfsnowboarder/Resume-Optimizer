"""
Handles extracting plain text from uploaded resume files (PDF or DOCX).

Streamlit gives us an "uploaded file" object when a user uploads something.
These functions take that object and return the text inside it as a string,
so the rest of the app doesn't need to care whether the original file was
a PDF or a Word document.
"""

import pdfplumber
from docx import Document


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from a PDF file uploaded via Streamlit."""
    text_parts = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # some pages might be blank/unreadable
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(uploaded_file) -> str:
    """Extract all text from a Word (.docx) file uploaded via Streamlit."""
    document = Document(uploaded_file)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text(uploaded_file) -> str:
    """
    Figures out the file type based on its name and calls the right
    extractor. This is the function the rest of the app should use.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        raise ValueError(
            f"Unsupported file type: {filename}. Please upload a .pdf or .docx file."
        )
