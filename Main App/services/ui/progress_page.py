import streamlit as st
from services.persistence.exercise_repository import get_users_exercises, get_users_form_issues
from services.tracking.progress_stats import (
    exercises_to_df, issues_to_df, summary_stats, daily_reps, issues_per_10_reps, top_issues,
)


def render_progress_page():
    with st.sidebar:
        st.divider()
        st.subheader("Progress")

    st.title("Your Progress")
    st.markdown("#### Workouts, streaks and how your form is improving")

    user_id = st.session_state.get("user_id")

    if not isinstance(user_id, int):
        st.info("Log in to see your progress.")
        return

    ex_df = exercises_to_df(get_users_exercises(user_id))
    issue_df = issues_to_df(get_users_form_issues(user_id))

    if ex_df.empty:
        st.info("No workouts yet. Complete a live workout or save a video analysis to see your progress here.")
        return

    stats = summary_stats(ex_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total reps", stats["total_reps"])
    col2.metric("Current streak", f"{stats['streak']} day{'s' if stats['streak'] != 1 else ''}")
    col3.metric("Active days", stats["active_days"])

    col4, col5, _ = st.columns(3)
    col4.metric("Workout time", f"{stats['total_minutes']} min")
    col5.metric("Plank held", f"{stats['plank_seconds']} s")

    st.divider()

    st.markdown("#### Reps per day (last 30 days)")
    reps_df = daily_reps(ex_df)

    if reps_df.empty:
        st.caption("No rep-based workouts in the last 30 days.")
    else:
        st.bar_chart(reps_df)

    st.markdown("#### Form issues per 10 reps")
    st.caption("Lower is better. A falling line means your form is improving.")
    rate_df = issues_per_10_reps(ex_df, issue_df)

    if rate_df.empty:
        st.caption("Not enough data yet.")
    else:
        st.line_chart(rate_df)

    st.markdown("#### Most common form issues")
    top_df = top_issues(issue_df)

    if top_df.empty:
        st.success("No form issues recorded yet.")
    else:
        st.table(top_df)
