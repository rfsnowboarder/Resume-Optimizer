"""
Main Streamlit app for the Resume & Job Description Optimizer.

Run this with:  streamlit run app.py

Phase 1 scope: upload a resume, paste a job description, see which
skills match, which are missing, and a basic match score.
"""

import streamlit as st
import pandas as pd

from src.parsing.document_parser import extract_text
from src.matching.keyword_matcher import compare_resume_to_jd
from src.ai.claude_client import get_ai_feedback
from src.ats_check.formatting_rules import run_ats_checks
from src.analytics.db import init_db, log_comparison, get_history_df, get_missing_skill_frequency

init_db()

st.set_page_config(page_title="Resume Optimizer", page_icon="📄")

st.title("📄 Resume & Job Description Optimizer")
st.write(
    "Upload your resume and paste a job description to see how well "
    "they match, based on key skills and keywords."
)

# --- Inputs ---
resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
jd_text_input = st.text_area("Paste the job description here", height=250)

col_a, col_b = st.columns(2)
with col_a:
    job_title_input = st.text_input("Job title (optional, for your own tracking)")
with col_b:
    company_input = st.text_input("Company (optional, for your own tracking)")

# --- Action ---
if st.button("Compare"):
    if resume_file is None:
        st.warning("Please upload a resume first.")
    elif not jd_text_input.strip():
        st.warning("Please paste a job description.")
    else:
        with st.spinner("Reading your resume..."):
            try:
                resume_text = extract_text(resume_file)
            except ValueError as e:
                st.error(str(e))
                st.stop()

        if not resume_text.strip():
            st.error(
                "Couldn't extract any text from that file. "
                "It might be a scanned/image-based PDF."
            )
            st.stop()

        results = compare_resume_to_jd(resume_text, jd_text_input)
        ats_report = run_ats_checks(resume_text)

        log_comparison(
            job_title=job_title_input,
            company=company_input,
            match_score=results["match_score"],
            matched_skills=results["matched_skills"],
            missing_skills=results["missing_skills"],
            ats_issue_count=len(ats_report["issues"]),
        )

        # Save everything in session_state so it survives the rerun that
        # happens when the user later clicks the "Get AI Feedback" button.
        st.session_state["resume_text"] = resume_text
        st.session_state["jd_text"] = jd_text_input
        st.session_state["results"] = results
        st.session_state["ats_report"] = ats_report

# --- Results display (reads from session_state so it persists across reruns) ---
if "results" in st.session_state:
    results = st.session_state["results"]

    st.subheader("Results")
    st.metric("Match Score", f"{results['match_score']}%")

    col1, col2 = st.columns(2)

    with col1:
        st.write("✅ **Matched skills**")
        if results["matched_skills"]:
            for skill in results["matched_skills"]:
                st.write(f"- {skill}")
        else:
            st.write("_None found_")

    with col2:
        st.write("⚠️ **Missing skills (in JD, not in resume)**")
        if results["missing_skills"]:
            for skill in results["missing_skills"]:
                st.write(f"- {skill}")
        else:
            st.write("_None — great coverage!_")

    with st.expander("Skills in your resume not mentioned in this JD"):
        if results["extra_skills"]:
            for skill in results["extra_skills"]:
                st.write(f"- {skill}")
        else:
            st.write("_None_")

    # --- ATS formatting check section ---
    st.subheader("ATS Formatting Check")
    st.caption(
        "Rule-based checks for common issues that trip up Applicant "
        "Tracking Systems. No AI involved here — just pattern checks."
    )

    ats_report = st.session_state["ats_report"]
    if ats_report["issues"]:
        st.warning(f"{len(ats_report['issues'])} potential issue(s) found:")
        for issue in ats_report["issues"]:
            st.write(f"- {issue}")
    else:
        st.success("No major ATS formatting issues detected!")

    # --- AI-powered feedback section ---
    st.subheader("AI-Powered Feedback")
    st.caption(
        "Get a deeper assessment of experience fit and tailored rewrite "
        "suggestions, powered by Claude. This uses your API credits."
    )

    if st.button("Get AI Feedback"):
        with st.spinner("Asking Claude for feedback... this may take a moment"):
            try:
                feedback = get_ai_feedback(
                    st.session_state["resume_text"], st.session_state["jd_text"]
                )
                st.markdown(feedback)
            except RuntimeError as e:
                st.error(str(e))

# --- Job Search Analytics Dashboard ---
# This section is always visible (not tied to session_state) since it
# reads directly from the database — showing your history even after
# restarting the app.
st.divider()
st.header("📊 My Job Search Analytics")
st.caption(
    "Trends across every comparison you've run through this tool, "
    "pulled from your local history database."
)

history_df = get_history_df()

if history_df.empty:
    st.info("No comparisons logged yet. Run a comparison above to start building your history.")
else:
    st.subheader(f"History ({len(history_df)} comparisons logged)")
    st.dataframe(
        history_df[["timestamp", "job_title", "company", "match_score", "ats_issue_count"]],
        use_container_width=True,
    )

    st.subheader("Match Score Over Time")
    chart_df = history_df.copy()
    chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"])
    chart_df = chart_df.sort_values("timestamp").set_index("timestamp")
    st.line_chart(chart_df["match_score"])

    st.subheader("Skills You're Missing Most Often")
    st.caption("Aggregated across all logged comparisons — these are the gaps worth addressing first.")
    skill_freq = get_missing_skill_frequency()
    if not skill_freq.empty:
        st.bar_chart(skill_freq.set_index("skill")["count"].head(10))
    else:
        st.write("_No missing skills logged yet — great sign!_")
