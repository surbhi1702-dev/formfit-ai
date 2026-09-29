import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True
    
    st.markdown(
        """
        <div class="ff-hero">
            <div class="ff-brand">
                <div class="ff-logo">🏋️</div>
                <div class="ff-brand-name">Form<span>Fit</span> AI</div>
            </div>
            <h2 style="margin-top:14px;">Your AI form coach</h2>
            <p>Real-time rep counting, form checks and voice coaching for 8 exercises,
            straight from your webcam or a recorded video.</p>
            <div class="ff-chips">
                <span class="ff-chip">Live pose tracking</span>
                <span class="ff-chip">Video analysis</span>
                <span class="ff-chip">AI voice coach</span>
                <span class="ff-chip">Progress dashboard</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("##### Enter a username to start")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Name (unique)", placeholder="e.g. alex")
        submit_button = st.form_submit_button("Let's Go", width="stretch")

    if submit_button:
        if not username:
            st.error("Name cannot be empty.")
            return False
        
        user = get_or_create_user(username)
    
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]

        st.rerun()

    return False
