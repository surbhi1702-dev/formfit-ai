"""Pure data helpers for the Progress dashboard (no Streamlit, easy to test)."""
from datetime import datetime, timedelta, timezone
import pandas as pd
from services.config.workout_config import TIME_BASED_EXERCISES


def exercises_to_df(rows):
    df = pd.DataFrame([
        {
            "Exercise": row["exercise_name"],
            "Reps": row["reps"],
            "Sets": row["sets"],
            "Time (sec)": row["time"] or 0,
            "Date": row["created_at"],
        }
        for row in rows
    ], columns=["Exercise", "Reps", "Sets", "Time (sec)", "Date"])

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

    return df


def issues_to_df(rows):
    df = pd.DataFrame([
        {
            "Exercise": row["exercise_name"],
            "Issue": row["issue"],
            "Count": row["count"],
            "Source": row["source"],
            "Date": row["created_at"],
        }
        for row in rows
    ], columns=["Exercise", "Issue", "Count", "Source", "Date"])

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

    return df


def today_utc():
    # The database stores CURRENT_TIMESTAMP in UTC, so compare against UTC dates
    return datetime.now(timezone.utc).date()


def compute_streak(dates, today=None):
    """Consecutive active days ending today (or yesterday, so a streak isn't lost before today's workout)."""
    today = today or today_utc()
    active = set(dates)

    if today in active:
        day = today
    elif today - timedelta(days=1) in active:
        day = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while day in active:
        streak += 1
        day -= timedelta(days=1)

    return streak


def summary_stats(ex_df, today=None):
    if ex_df.empty:
        return {"total_reps": 0, "plank_seconds": 0, "active_days": 0, "streak": 0, "total_minutes": 0}

    rep_based = ex_df[~ex_df["Exercise"].isin(TIME_BASED_EXERCISES)]
    time_based = ex_df[ex_df["Exercise"].isin(TIME_BASED_EXERCISES)]

    return {
        "total_reps": int(rep_based["Reps"].sum()),
        "plank_seconds": int(time_based["Reps"].sum()),
        "active_days": int(ex_df["Date"].nunique()),
        "streak": compute_streak(ex_df["Date"].unique(), today),
        "total_minutes": int(ex_df["Time (sec)"].sum() // 60),
    }


def daily_reps(ex_df, days=30, today=None):
    """Reps per day per exercise (rep-based exercises only), for the last `days` days."""
    today = today or today_utc()
    rep_based = ex_df[~ex_df["Exercise"].isin(TIME_BASED_EXERCISES)]

    if rep_based.empty:
        return pd.DataFrame()

    since = today - timedelta(days=days - 1)
    recent = rep_based[rep_based["Date"] >= since]

    if recent.empty:
        return pd.DataFrame()

    return recent.pivot_table(index="Date", columns="Exercise", values="Reps", aggfunc="sum", fill_value=0)


def issues_per_10_reps(ex_df, issue_df):
    """Form issues per 10 reps, per day. Lower is better — shows whether form is improving."""
    rep_based = ex_df[~ex_df["Exercise"].isin(TIME_BASED_EXERCISES)]

    if rep_based.empty:
        return pd.DataFrame()

    reps_by_day = rep_based.groupby("Date")["Reps"].sum()

    if issue_df.empty:
        issues_by_day = pd.Series(0, index=reps_by_day.index)
    else:
        rep_issues = issue_df[~issue_df["Exercise"].isin(TIME_BASED_EXERCISES)]
        issues_by_day = rep_issues.groupby("Date")["Count"].sum().reindex(reps_by_day.index, fill_value=0)

    rate = (issues_by_day / reps_by_day.where(reps_by_day > 0) * 10).fillna(0).round(1)

    return rate.to_frame("Issues per 10 reps")


def top_issues(issue_df, limit=5):
    if issue_df.empty:
        return pd.DataFrame(columns=["Exercise", "Issue", "Times"])

    top = (
        issue_df.groupby(["Exercise", "Issue"])["Count"].sum()
        .sort_values(ascending=False)
        .head(limit)
        .reset_index()
        .rename(columns={"Count": "Times"})
    )
    top.index += 1

    return top
