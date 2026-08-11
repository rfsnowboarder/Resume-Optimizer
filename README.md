# 📄 AI Resume & Job Description Optimizer

A Python web app that compares your resume against a job description, identifies skill gaps, checks ATS (Applicant Tracking System) formatting compatibility, generates AI-powered rewrite suggestions, and tracks trends across your job search using a local SQL database.

**[Live demo →](#)** *(link once deployed)*

![App screenshot placeholder](docs/screenshot.png)
*(Add a screenshot or GIF of the app here once you have one — this matters a lot for first impressions.)*

---

## Why I Built This

I built this project to solve a recurring problem in my own job search: spending time on applications that turned out to be a poor match, often because I lacked specific required experience. My goal was to reduce that wasted time by quickly identifying which job postings genuinely align with my skill set, and to generate tailored resume rewrites that better match each job description for the applications I do pursue.

I chose this approach because I wanted a project that would keep providing value after I built it; not just a portfolio piece, but a tool I'd actually use in my day-to-day job search. Along the way, I also wanted to improve at writing a stronger, more tailored resume, while saving time by filtering out applications I could quickly identify as bad fits.

---

## Features

- **Skill Gap Matching** — Extracts and compares skills/keywords between your resume and a job description, with a match score
- **ATS Formatting Checks** — Rule-based detection of common issues that trip up real Applicant Tracking Systems (missing sections, missing contact info, layout artifacts)
- **AI-Powered Feedback** — Uses the Claude API to assess experience-level fit and generate tailored, truthful rewrite suggestions (with guardrails against fabricating experience)
- **Job Search Analytics** — Every comparison is logged to a local SQLite database; a dashboard shows match score trends over time and your most frequently missing skills, powered by SQL queries and pandas

---

## Key Findings From My Own Job Search

*(Fill this in once you've used the tool for real applications — this section is what turns the project from "a tool I built" into "an analysis I did." Example format below.)*

> Across `[N]` job applications I compared, `[skill]` appeared as a gap in `[X]%` of postings. My average match score was `[X]%`, improving to `[X]%` after applying the AI's rewrite suggestions.

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| Document parsing | `pdfplumber`, `python-docx` |
| Skill matching | Custom rule-based matcher (Python, regex) |
| AI feedback | [Claude API](https://www.anthropic.com) (Sonnet) |
| Data storage & analysis | SQLite, `pandas`, raw SQL queries |
| Testing | `pytest` |

---

## Project Structure

```
resume-optimizer/
├── app.py                     # Streamlit entry point
├── src/
│   ├── parsing/                # PDF/DOCX text extraction
│   ├── matching/                # Keyword/skill gap logic
│   ├── ats_check/                # Rule-based ATS formatting checks
│   ├── ai/                       # Claude API integration
│   └── analytics/                # SQLite logging + pandas analysis
├── tests/                     # pytest unit tests
├── db/                        # SQLite database (gitignored — personal data)
├── requirements.txt
└── .env                       # API key (gitignored, never committed)
```

---

## Running It Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/resume-optimizer.git
cd resume-optimizer
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up your API key**

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_key_here
```
Get a key at [console.anthropic.com](https://console.anthropic.com).

**4. Run the app**
```bash
streamlit run app.py
```

---

## Running the Tests

```bash
pytest
```

---

## Design Decisions & Limitations

- **Keyword matching is deterministic on purpose** — the skill-matching layer is plain rule-based code, not AI. This keeps it fast, free, and predictable; AI is reserved for the parts that genuinely need reasoning (experience-level assessment, rewrite generation).
- **The AI is instructed never to invent experience** — the system prompt explicitly forbids fabricating achievements or metrics the resume doesn't already contain, since a resume tool that lies for you is worse than useless.
- **ATS checks work from extracted text, not the original file layout** — since the app only has access to parsed text, formatting checks look for *symptoms* of layout problems (e.g. garbled or run-together text) rather than directly inspecting the visual layout.
- **v1 doesn't evaluate years-of-experience depth in the keyword matcher** — a resume that mentions "SQL" once currently matches the same as one with 5 years of SQL experience in Phase 1's scoring. This is addressed in the AI feedback layer, which reasons about depth rather than just presence.

---

## What I'd Do With More Time

*(Good spot to list 2-3 honest next steps — shows self-awareness and forward thinking, which reviewers like. E.g. semantic/synonym-aware matching instead of exact keyword match, multi-resume comparison, exporting tailored resume versions, etc.)*

---

## License

MIT
