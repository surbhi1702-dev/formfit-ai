import streamlit as st

# FormFit colour palette (dark theme, WCAG-friendly contrast)
ACCENT = "#22c55e"
ACCENT_DARK = "#16a34a"
ACCENT_SOFT = "rgba(34, 197, 94, 0.12)"
BG = "#0b0f19"            # page background
SURFACE = "#111827"       # cards, sidebar, uploader
SURFACE_2 = "#1f2937"     # inputs, dropdowns
BORDER = "#374151"
TEXT = "#f3f4f6"          # main text
TEXT_SOFT = "#d1d5db"     # labels
TEXT_MUTED = "#9ca3af"    # captions, hints


def inject_formfit_theme():
    """FormFit theme. Overrides every text colour so nothing is dark-on-dark."""
    st.markdown(
        f"""
        <style>
        /* ---------- Page, header, sidebar ---------- */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            background-color: {BG} !important;
            color: {TEXT} !important;
        }}
        [data-testid="stHeader"] {{
            background-color: {BG} !important;
        }}
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div {{
            background-color: {SURFACE} !important;
            border-right: 1px solid rgba(34, 197, 94, 0.25);
        }}

        /* ---------- All text ---------- */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp p, .stApp li, .stApp span, .stApp label, .stApp strong,
        [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] * {{
            color: {TEXT} !important;
            opacity: 1 !important;
        }}

        /* Labels of inputs (Name, Exercise, Sets, Workout video, Mode...) */
        [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] * {{
            color: {TEXT_SOFT} !important;
            opacity: 1 !important;
        }}

        /* Captions and hints */
        [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
        .ff-tagline {{
            color: {TEXT_MUTED} !important;
            opacity: 1 !important;
        }}

        /* ---------- Inputs ---------- */
        .stTextInput input, .stNumberInput input, [data-baseweb="input"] input,
        [data-baseweb="select"] > div, [data-baseweb="select"] * {{
            background-color: {SURFACE_2} !important;
            color: {TEXT} !important;
            border-color: {BORDER} !important;
        }}
        .stTextInput input::placeholder, .stNumberInput input::placeholder {{
            color: {TEXT_MUTED} !important;
        }}
        .stNumberInput button {{
            background-color: {SURFACE_2} !important;
            color: {TEXT} !important;
            border-color: {BORDER} !important;
        }}
        .stNumberInput button svg {{ fill: {TEXT} !important; }}

        /* Dropdown menu */
        [data-baseweb="popover"] ul, [data-baseweb="popover"] li,
        [data-baseweb="menu"], [data-baseweb="menu"] * {{
            background-color: {SURFACE_2} !important;
            color: {TEXT} !important;
        }}
        [data-baseweb="menu"] li:hover {{ background-color: {BORDER} !important; }}

        /* Radio buttons */
        .stRadio label p {{ color: {TEXT} !important; }}

        /* File uploader */
        [data-testid="stFileUploaderDropzone"] {{
            background-color: {SURFACE} !important;
            border: 1px dashed {BORDER} !important;
        }}
        [data-testid="stFileUploaderDropzone"] *,
        [data-testid="stFileUploaderFile"] * {{
            color: {TEXT_SOFT} !important;
            opacity: 1 !important;
        }}
        [data-testid="stFileUploaderDropzone"] button {{
            background-color: {SURFACE_2} !important;
            color: {TEXT} !important;
            border: 1px solid {BORDER} !important;
        }}

        /* ---------- Buttons ---------- */
        .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
            background: linear-gradient(135deg, {ACCENT} 0%, {ACCENT_DARK} 100%) !important;
            color: #06130b !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            opacity: 1 !important;
            transition: transform 0.08s ease, box-shadow 0.2s ease;
        }}
        .stButton > button *, .stFormSubmitButton > button *, .stDownloadButton > button * {{
            color: #06130b !important;
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            box-shadow: 0 6px 18px rgba(34, 197, 94, 0.35);
            transform: translateY(-1px);
        }}

        /* ---------- Forms and cards ---------- */
        [data-testid="stForm"] {{
            background-color: {SURFACE} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 12px !important;
        }}
        [data-testid="stMetric"] {{
            background-color: {SURFACE} !important;
            border: 1px solid {BORDER} !important;
            border-left: 3px solid {ACCENT} !important;
            border-radius: 10px !important;
            opacity: 1 !important;
        }}
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {{
            color: {TEXT_SOFT} !important;
            font-weight: 500 !important;
            opacity: 1 !important;
        }}
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {{
            color: {TEXT} !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }}

        /* ---------- Alerts (info, success, warning, error) ---------- */
        [data-testid="stAlert"] {{ border-radius: 10px !important; }}
        [data-testid="stAlertContentInfo"], [data-testid="stAlertContentInfo"] * {{ color: #bfdbfe !important; }}
        [data-testid="stAlertContentSuccess"], [data-testid="stAlertContentSuccess"] * {{ color: #bbf7d0 !important; }}
        [data-testid="stAlertContentWarning"], [data-testid="stAlertContentWarning"] * {{ color: #fde68a !important; }}
        [data-testid="stAlertContentError"], [data-testid="stAlertContentError"] * {{ color: #fecaca !important; }}

        /* ---------- Tables, expanders, charts, dividers ---------- */
        .stApp table {{ background-color: {SURFACE} !important; }}
        .stApp table th, .stApp table td {{
            color: {TEXT} !important;
            border-color: {BORDER} !important;
            background-color: transparent !important;
        }}
        .stApp table th {{ color: {TEXT_SOFT} !important; font-weight: 600 !important; }}
        [data-testid="stExpander"] {{
            background-color: {SURFACE} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 10px !important;
        }}
        [data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{
            color: {TEXT} !important;
        }}
        [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] {{
            background-color: {SURFACE} !important;
            border-radius: 10px !important;
            padding: 8px !important;
        }}
        .stApp hr {{ border-color: {BORDER} !important; }}
        [data-testid="stProgress"] > div > div > div > div {{
            background-color: {ACCENT} !important;
        }}

        /* ---------- Icons: keep Streamlit's icon font (the base stylesheet overrides it) ---------- */
        [data-testid="stIconMaterial"], [data-testid="stExpanderIcon"],
        span[class*="material-symbols"], .material-symbols-rounded {{
            font-family: "Material Symbols Rounded" !important;
            font-feature-settings: "liga" !important;
            -webkit-font-feature-settings: "liga" !important;
            color: {TEXT_SOFT} !important;
        }}

        /* ---------- FormFit custom blocks ---------- */
        .ff-brand {{ display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }}
        .ff-logo {{
            width: 38px; height: 38px; border-radius: 10px;
            background: linear-gradient(135deg, {ACCENT} 0%, {ACCENT_DARK} 100%);
            display: flex; align-items: center; justify-content: center; font-size: 20px;
        }}
        .ff-brand-name {{ font-size: 1.35rem; font-weight: 700; color: {TEXT} !important; }}
        .ff-brand-name span, .stApp .ff-brand-name span {{ color: {ACCENT} !important; }}
        .ff-tagline {{ font-size: 0.8rem; margin-top: -2px; }}

        .ff-hero {{
            border-radius: 16px; padding: 28px 28px 22px 28px; margin: 18px 0 8px 0;
            background: radial-gradient(circle at top right, {ACCENT_SOFT}, transparent 60%), {SURFACE};
            border: 1px solid rgba(34, 197, 94, 0.3);
        }}
        .ff-hero h2 {{ margin: 0 0 6px 0; }}
        .stApp .ff-hero p {{ color: {TEXT_SOFT} !important; margin: 0; }}

        .ff-steps {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px; margin: 16px 0 24px 0;
        }}
        .ff-step {{
            border-radius: 12px; padding: 16px;
            background: {SURFACE}; border: 1px solid {BORDER};
        }}
        .stApp .ff-step-num {{
            display: inline-block; width: 26px; height: 26px; line-height: 26px;
            border-radius: 50%; text-align: center; font-weight: 700; font-size: 0.85rem;
            background: {ACCENT_SOFT}; color: {ACCENT} !important; margin-bottom: 8px;
        }}
        .ff-step-title {{ font-weight: 600; margin-bottom: 4px; }}
        .stApp .ff-step-text {{ font-size: 0.85rem; color: {TEXT_MUTED} !important; }}

        .ff-chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
        .stApp .ff-chip {{
            font-size: 0.78rem; padding: 4px 10px; border-radius: 999px;
            background: {ACCENT_SOFT}; color: #86efac !important;
            border: 1px solid rgba(34, 197, 94, 0.35);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand():
    st.markdown(
        """
        <div class="ff-brand">
            <div class="ff-logo">🏋️</div>
            <div>
                <div class="ff-brand-name">Form<span>Fit</span> AI</div>
                <div class="ff-tagline">Train smarter. Move better.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_hero(exercises):
    chips = "".join(f'<span class="ff-chip">{name}</span>' for name in exercises)

    st.markdown(
        f"""
        <div class="ff-hero">
            <h2>Ready when you are 💪</h2>
            <p>Pick an exercise in the sidebar and FormFit will count your reps,
            check your form in real time and coach you by voice.</p>
            <div class="ff-chips">{chips}</div>
        </div>
        <div class="ff-steps">
            <div class="ff-step">
                <div class="ff-step-num">1</div>
                <div class="ff-step-title">Plan</div>
                <div class="ff-step-text">Choose an exercise, sets and reps in the sidebar.</div>
            </div>
            <div class="ff-step">
                <div class="ff-step-num">2</div>
                <div class="ff-step-title">Train</div>
                <div class="ff-step-text">Start the camera, or switch to Upload Video to analyse a recording.</div>
            </div>
            <div class="ff-step">
                <div class="ff-step-num">3</div>
                <div class="ff-step-title">Improve</div>
                <div class="ff-step-text">Get live form feedback, then track progress in the dashboard.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
