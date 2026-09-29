import os
import tempfile
import pandas as pd
import streamlit as st
from services.config.workout_config import EXERCISE_OPTIONS
from services.vision.video_file_analyzer import analyze_video
from services.persistence.exercise_repository import add_exercise, add_form_issue


def render_video_upload():
    with st.sidebar:
        st.divider()
        st.subheader("Video Analysis")

        st.markdown(
            "Upload a recorded workout and get rep counts and form feedback "
            "without a live camera."
        )

    st.title("Video Form Analysis")
    st.markdown("#### Upload a workout video to count reps and detect form issues")

    exercise = st.selectbox("Exercise in the video", options=EXERCISE_OPTIONS, key="video_exercise")

    uploaded = st.file_uploader(
        "Workout video",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        key="video_file",
    )

    st.caption(
        "Tips: one person in frame, full body visible, steady camera. "
        "A side view works best for squats, push-ups, lunges, plank and sit-ups."
    )

    if uploaded and st.button("Analyze Video", width="stretch", key="analyze_video_button"):
        suffix = os.path.splitext(uploaded.name)[1] or ".mp4"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.getbuffer())
            video_path = tmp.name

        progress = st.progress(0.0, text="Analyzing video...")

        try:
            result = analyze_video(
                video_path,
                exercise,
                progress_callback=lambda p: progress.progress(p, text=f"Analyzing video... {int(p * 100)}%"),
            )
            st.session_state.video_result = result
        except Exception as e:
            st.session_state.video_result = None
            st.error(f"Could not analyze this video: {e}")
        finally:
            progress.empty()
            os.remove(video_path)

    result = st.session_state.get("video_result")

    if result:
        _render_results(result)


def _render_results(result):
    st.divider()
    st.subheader(f"Results: {result['exercise']}")

    if result["pose_frames"] == 0:
        st.error("No person was detected in this video. Make sure your full body is visible.")
        return

    pose_pct = int(100 * result["pose_frames"] / max(result["frames_analysed"], 1))

    col1, col2, col3 = st.columns(3)
    if result.get("time_based"):
        col1.metric("Held in good form", f"{result['reps']} s")
    else:
        col1.metric("Reps counted", result["reps"])
    col2.metric("Video length", f"{result['duration']:.1f} s")
    col3.metric("Body detected", f"{pose_pct}%")

    if pose_pct < 50:
        st.warning("Your body was only detected in part of the video, so counts may be low.")

    st.markdown("#### Joint angle over time")
    angle_df = pd.DataFrame(result["angle_series"]).set_index("Time (s)")
    st.line_chart(angle_df, y=result["angle_label"])

    if result["rep_times"]:
        times = ", ".join(f"{t}s" for t in result["rep_times"])
        st.caption(f"Reps completed at: {times}")

    _render_save_button(result)

    st.markdown("#### Form issues")

    if not result["issue_counts"]:
        st.success("No form issues detected. Nice work!")
        return

    for issue, count in sorted(result["issue_counts"].items(), key=lambda x: -x[1]):
        label = "time" if count == 1 else "times"

        with st.expander(f"{issue} ({count} {label})"):
            t, image = result["issue_snapshots"][issue]
            st.image(image, caption=f"First seen at {t}s")


def _render_save_button(result):
    user_id = st.session_state.get("user_id")

    if not isinstance(user_id, int):
        return

    if result.get("saved"):
        st.caption("✅ Saved to your workout history and progress.")
        return

    if st.button("Save to my history", key="save_video_result"):
        if result["reps"] > 0:
            add_exercise(user_id, result["exercise"], result["reps"], 1, int(result["duration"]))

        for issue, count in result["issue_counts"].items():
            add_form_issue(user_id, result["exercise"], issue, count, "video")

        result["saved"] = True
        st.rerun()
