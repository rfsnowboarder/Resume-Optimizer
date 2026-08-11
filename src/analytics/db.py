"""
Handles storing and retrieving a history of every resume/JD comparison
run through the app, using SQLite.

Why SQLite: it's a real relational database (not just a CSV), it ships
with Python (no separate server to install/run), and it lets us write
actual SQL queries for analysis — which is the point of this module.
It stores everything in a single file (db/history.db) that lives in
your project folder.
"""

import os
import sqlite3
import tempfile
from datetime import datetime

import pandas as pd

# Streamlit Cloud's app source folder is read-only, so we can't write a
# database file there. Python's temp directory is always writable, both
# locally and on Streamlit Cloud, so we use that instead.
#
# Note: on Streamlit Cloud, this means history resets whenever the app
# restarts/sleeps — that's expected and fine for a public demo. Your
# real job-search tracking should happen on your local copy of the app,
# where this same temp-directory approach still works but tends to
# persist much longer between restarts.
DB_PATH = os.path.join(tempfile.gettempdir(), "resume_optimizer_history.db")


def init_db(db_path: str = DB_PATH) -> None:
    """
    Creates the history table if it doesn't already exist. Safe to call
    every time the app starts — it won't wipe existing data.
    """
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            job_title TEXT,
            company TEXT,
            match_score INTEGER NOT NULL,
            matched_skills TEXT,
            missing_skills TEXT,
            ats_issue_count INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


def log_comparison(
    job_title: str,
    company: str,
    match_score: int,
    matched_skills: list,
    missing_skills: list,
    ats_issue_count: int,
    db_path: str = DB_PATH,
) -> None:
    """
    Inserts one row representing a single resume/JD comparison run.
    Skill lists are stored as comma-separated text since SQLite doesn't
    have a native list type — this is a common, simple approach for
    small projects like this.
    """
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO history
            (timestamp, job_title, company, match_score, matched_skills, missing_skills, ats_issue_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            job_title,
            company,
            match_score,
            ", ".join(matched_skills),
            ", ".join(missing_skills),
            ats_issue_count,
        ),
    )
    conn.commit()
    conn.close()


def get_history_df(db_path: str = DB_PATH) -> pd.DataFrame:
    """
    Returns the full comparison history as a pandas DataFrame,
    ordered most-recent first. This is what the analytics dashboard
    and any exploratory analysis will read from.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM history ORDER BY timestamp DESC", conn)
    conn.close()
    return df


def get_missing_skill_frequency(db_path: str = DB_PATH) -> pd.DataFrame:
    """
    Runs a SQL query to pull all logged missing_skills, then uses pandas
    to split and count them — answering "which skills show up as gaps
    most often across all the jobs I've checked?"

    Returns a DataFrame with columns: skill, count — sorted most frequent first.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT missing_skills FROM history WHERE missing_skills != ''", conn
    )
    conn.close()

    if df.empty:
        return pd.DataFrame(columns=["skill", "count"])

    # Each row's missing_skills is a comma-separated string; split it into
    # a list per row, then "explode" so each skill gets its own row.
    all_skills = (
        df["missing_skills"]
        .str.split(", ")
        .explode()
        .str.strip()
    )
    counts = all_skills.value_counts().reset_index()
    counts.columns = ["skill", "count"]
    return counts
