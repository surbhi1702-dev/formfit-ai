import streamlit as st


def initial_session_defaults():
    defaults = {
        "reps": 0,
        "target_sets": 0,
        "reps_per_set": 0,
        "sets_completed": 0,
        "current_set_reps": 0,
        "workout_complete": False,
        "last_notified_sets_completed": 0,
        "last_notified_workout_complete": False,
        "last_saved_sets_completed": 0,
        "set_cycle_started_at": 0.0,
        "last_exercise_type": "Squats",

        # Workout plan (set before starting)
        "workout_started": False,
        "plan_exercise": "Squats",
        "plan_sets": 3,
        "plan_reps": 10,

        # Common Angles
        "knee_angle": 0,
        "back_angle": 0,
        "elbow_angle": 0,
        "front_knee_angle": 0,
        "torso_angle": 0,

        # Status fields
        "depth_status": "N/A",
        "body_alignment": "N/A",
        "hip_status": "N/A",
        "shoulder_status": "N/A",
        "swing_status": "N/A",
        "extension_status": "N/A",
        "back_arch_status": "N/A",
        "balance_status": "N/A",

        # New exercises
        "hold_time": 0,
        "body_angle": 0,
        "plank_status": "N/A",
        "arm_angle": 0,
        "arm_status": "N/A",
        "leg_status": "N/A",
        "rep_quality": "N/A",
        "hip_angle": 0,
        "knee_status": "N/A",
        "torso_lean": 0,

        # Live form-issue logging
        "issue_pending": None,
        "issue_pending_since": 0.0,
        "issue_pending_logged": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
