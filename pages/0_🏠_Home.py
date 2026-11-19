
import streamlit as st

st.set_page_config(
    page_title="Smart FAQ Bot | Government Scheme Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');

.stApp {
    background: #F5F7FA;
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.hero {
    background: linear-gradient(125deg, #071F38, #0B3D68 65%, #12527C);
    border: 1px solid #C99A3E;
    border-radius: 22px;
    padding: 65px 55px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 15px 40px rgba(7,31,56,0.18);
}

.hero:after {
    content: "";
    position: absolute;
    width: 320px;
    height: 320px;
    border: 1px solid rgba(226,190,105,0.25);
    border-radius: 50%;
    right: -100px;
    top: -150px;
}

.eyebrow {
    color: #E5C477;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero h1 {
    color: white;
    font-family: 'Playfair Display', serif;
    font-size: clamp(38px, 5vw, 60px);
    line-height: 1.15;
    margin: 22px 0 15px;
}

.hero p {
    color: #DCE8F2;
    font-size: 17px;
    line-height: 1.8;
    max-width: 680px;
}

.gold-line {
    width: 75px;
    height: 4px;
    background: #D6AC54;
    border-radius: 10px;
    margin: 22px 0;
}

.section-title {
    color: #0B3154;
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    font-weight: 700;
}

.feature-card {
    background: white;
    border: 1px solid #E1E7EF;
    border-radius: 15px;
    padding: 24px 21px;
    min-height: 175px;
    box-shadow: 0 5px 16px rgba(12,42,70,0.045);
}

.feature-icon {
    font-size: 29px;
    margin-bottom: 12px;
}

.feature-card h3 {
    color: #123B60;
    font-size: 17px;
    margin: 0 0 9px;
}

.feature-card p {
    color: #687789;
    font-size: 13px;
    line-height: 1.7;
    margin: 0;
}

.info-strip {
    background: #EAF0F6;
    border-left: 4px solid #C99A3E;
    padding: 18px 22px;
    border-radius: 9px;
    color: #29445F;
    line-height: 1.7;
}

.footer {
    text-align: center;
    color: #7A8795;
    font-size: 12px;
    padding: 25px 0 5px;
    border-top: 1px solid #E1E7EF;
}

div.stButton > button {
    background: #D0A447;
    color: #102D49;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    padding: 13px 25px;
    min-height: 48px;
}

div.stButton > button:hover {
    background: #E2BC6D;
    color: #102D49;
    border: none;
}
</style>
""", unsafe_allow_html=True)


# NAVIGATION HEADER

left, right = st.columns([3, 1])

with left:
    st.markdown(
        "<h3 style='color:#103B61;margin:0;'>🏛️ SMART FAQ BOT</h3>"
        "<p style='color:#9A7837;font-size:11px;letter-spacing:1.5px;'>"
        "CITIZEN SERVICES · DIGITAL ASSISTANCE</p>",
        unsafe_allow_html=True
    )

with right:
    st.markdown(
        "<p style='text-align:right;color:#52677C;padding-top:8px;'>"
        "HOME &nbsp; | &nbsp; ABOUT</p>",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# HERO SECTION

st.markdown("""
<div class="hero">
    <div class="eyebrow">Your Digital Government Scheme Assistant</div>
    <h1>Government Schemes,<br>Made Simple.</h1>
    <div class="gold-line"></div>
    <p>
        Discover government scheme information, understand eligibility,
        explore benefits and find application guidance — all through
        one intelligent multilingual assistant.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# GET STARTED

col1, col2, col3 = st.columns([1, 1.2, 1])

with col2:
    if st.button("Get Started  →", use_container_width=True):
        st.switch_page("app.py")

st.markdown("<br>", unsafe_allow_html=True)


# FEATURES

st.markdown(
    "<div class='section-title'>Information made accessible to everyone.</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='color:#718096;'>"
    "Explore the capabilities of your Smart FAQ Bot."
    "</p>",
    unsafe_allow_html=True
)

features = [
    ("🌐", "Multilingual Support",
     "Ask questions in English, Hindi, Kannada, Tamil, Telugu and Malayalam."),
    ("🤖", "AI-Powered Assistance",
     "Get understandable answers using Groq and Gemini language models."),
    ("📄", "Document-Grounded Answers",
     "Answers are generated using the government scheme documents available in the system."),
    ("🎙️", "Voice Interaction",
     "Speak your questions instead of typing, with voice input and audio responses.")
]

cols = st.columns(4)

for col, feature in zip(cols, features):
    icon, title, description = feature
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# HOW IT HELPS

st.markdown("""
<div class="info-strip">
    <b>Our purpose</b><br>
    To make government scheme information easier to understand and
    accessible to citizens through a simple, multilingual,
    document-grounded AI assistant.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    SMART FAQ BOT · AI-POWERED CITIZEN ASSISTANCE<br>
    An academic project — not an official Government of India portal.
    Always verify scheme details with the relevant government authority.
</div>
""", unsafe_allow_html=True)
