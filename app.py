import os
import time
import sqlite3
import hashlib
from urllib.parse import quote_plus


import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareerPath AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# LOAD API KEY
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "page": "Dashboard",
    "roadmap": "",
    "profile_created": False,
    "logged_in": False,
    "user_id": None,
    "username": "",

    "name": "",
    "degree": "",
    "branch": "",
    "year": "",
    "target_career": "",
    "skill_level": "",
    "learning_hours": 10,
    "current_skills": "",
    "interests": "",
    "additional_info": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# DATABASE & AUTHENTICATION
# =========================================================

DB_FILE = "careerpath_users.db"


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


# Initialize the database after defining get_db()

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# Create the database once when the app starts
get_db()


def create_account(username, password):
    username = username.strip()
    if not username or not password:
        return False, "Username and password are required."
    if len(username) < 3:
        return False, "Username must contain at least 3 characters."
    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "This username already exists. Please choose another one."
    finally:
        conn.close()


def authenticate_user(username, password):
    conn = get_db()
    row = conn.execute(
        "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
        (username.strip(), hash_password(password))
    ).fetchone()
    conn.close()
    return row


def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.25, 1])

    with center:
        st.html("""
        <div class="auth-card">
            <div class="auth-logo">🎓</div>
            <div class="auth-title">CareerPath AI</div>
            <div class="auth-subtitle">Your personalized career learning platform</div>
            <div class="auth-welcome">Welcome Back 👋</div>
        </div>
        """)

        username = st.text_input("Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

        if st.button("🔐 Login", use_container_width=True, key="login_button"):
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.page = "Dashboard"
                st.success("Login successful! Welcome back 👋")
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.markdown("<div style='text-align:center;margin:18px 0;color:#64748b;'>Don't have an account?</div>", unsafe_allow_html=True)
        if st.button("📝 Create Account", use_container_width=True, key="go_register"):
            st.session_state.auth_page = "register"
            st.rerun()


def registration_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.25, 1])

    with center:
        st.html("""
        <div class="auth-card">
            <div class="auth-logo">🎓</div>
            <div class="auth-title">Create Account</div>
            <div class="auth-subtitle">Join CareerPath AI and start your career journey</div>
        </div>
        """)

        username = st.text_input("Choose Username", placeholder="Enter a username", key="register_username")
        password = st.text_input("Create Password", type="password", placeholder="At least 6 characters", key="register_password")
        confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="register_confirm")

        if st.button("✨ Register", use_container_width=True, key="register_button"):
            if password != confirm:
                st.error("Passwords do not match.")
            else:
                ok, message = create_account(username, password)
                if ok:
                    st.success(message)
                    st.session_state.auth_page = "login"
                    st.rerun()
                else:
                    st.error(message)

        st.markdown("<div style='text-align:center;margin:18px 0;color:#64748b;'>Already have an account?</div>", unsafe_allow_html=True)
        if st.button("← Back to Login", use_container_width=True, key="back_login"):
            st.session_state.auth_page = "login"
            st.rerun()

# =========================================================
# CSS
# =========================================================

st.html(
    """
    <style>

    /* ================================
       GLOBAL
       ================================ */

    .stApp {
        background:
            radial-gradient(
                circle at 80% 0%,
                rgba(99,102,241,0.12),
                transparent 25%
            ),
            #080c16;

        color: #f8fafc;
    }

    .main {
        padding: 25px 45px 50px 45px;
    }

    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* ================================
       SIDEBAR
       ================================ */

    section[data-testid="stSidebar"] {
        background: #0c1220;
        border-right: 1px solid #1d2638;
    }

    section[data-testid="stSidebar"] > div {
        padding: 20px 15px;
    }

    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 8px 25px 8px;
        border-bottom: 1px solid #202a3c;
        margin-bottom: 20px;
    }

    .sidebar-logo-icon {
        width: 43px;
        height: 43px;
        border-radius: 13px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: linear-gradient(
            135deg,
            #6366f1,
            #8b5cf6
        );

        font-size: 21px;
    }

    .sidebar-logo-title {
        font-size: 20px;
        font-weight: 800;
        color: white;
    }

    .sidebar-logo-subtitle {
        font-size: 11px;
        color: #64748b;
        margin-top: 2px;
    }


    /* ================================
       SIDEBAR BUTTONS
       ================================ */

    section[data-testid="stSidebar"] .stButton > button {

        background: transparent !important;

        border: none !important;

        color: #94a3b8 !important;

        text-align: left !important;

        justify-content: flex-start !important;

        width: 100% !important;

        height: 44px !important;

        padding: 0 13px !important;

        border-radius: 10px !important;

        font-size: 14px !important;

        font-weight: 600 !important;

        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {

        background: #151e30 !important;

        color: white !important;
    }


    /* ================================
       PROFILE SIDEBAR
       ================================ */

    .sidebar-profile {

        background: #111827;

        border: 1px solid #202a3c;

        border-radius: 14px;

        padding: 13px;

        margin-top: 25px;
    }

    .sidebar-profile-name {

        color: white;

        font-weight: 700;

        font-size: 13px;
    }

    .sidebar-profile-career {

        color: #818cf8;

        font-size: 11px;

        margin-top: 3px;
    }


    /* ================================
       PAGE HEADER
       ================================ */

    .page-header {
        margin-bottom: 28px;
    }

    .page-title {

        font-size: 34px;

        font-weight: 850;

        color: white;

        margin-bottom: 7px;
    }

    .page-subtitle {

        color: #94a3b8;

        font-size: 14px;
    }


    /* ================================
       CARDS
       ================================ */

    .content-card {

        background: #101827;

        border: 1px solid #202a3c;

        border-radius: 16px;

        padding: 22px;

        margin-bottom: 18px;
    }

    .content-card-title {

        color: white;

        font-size: 17px;

        font-weight: 750;

        margin-bottom: 10px;
    }

    .content-card-text {

        color: #94a3b8;

        font-size: 13px;

        line-height: 1.7;
    }


    /* ================================
       STAT CARDS
       ================================ */

    .stat-card {

        background: #101827;

        border: 1px solid #202a3c;

        border-radius: 16px;

        padding: 20px;

        min-height: 125px;
    }

    .stat-icon {

        font-size: 25px;

        margin-bottom: 8px;
    }

    .stat-number {

        color: white;

        font-size: 20px;

        font-weight: 800;
    }

    .stat-label {

        color: #64748b;

        font-size: 12px;

        margin-top: 4px;
    }


    /* ================================
       FORM
       ================================ */

    label {

        color: #cbd5e1 !important;

        font-weight: 600 !important;
    }

    .stTextInput input,
    .stTextArea textarea {

        background: #101827 !important;

        color: white !important;

        border: 1px solid #263244 !important;

        border-radius: 11px !important;
    }

    div[data-baseweb="select"] > div {

        background: #101827 !important;

        border: 1px solid #263244 !important;

        border-radius: 11px !important;
    }


    /* ================================
       BUTTONS
       ================================ */

    .stButton > button {

        border-radius: 11px !important;

        font-weight: 700 !important;

        min-height: 43px !important;
    }


    /* ================================
       ROADMAP
       ================================ */

    .roadmap-box {

        background: #101827;

        border: 1px solid #202a3c;

        border-radius: 16px;

        padding: 28px;

        color: #dbeafe;

        line-height: 1.8;

        font-size: 14px;
    }


    /* ================================
       VIDEO CARD
       ================================ */

    .video-card {

        background: #101827;

        border: 1px solid #202a3c;

        border-radius: 15px;

        padding: 20px;

        margin-bottom: 15px;
    }

    .video-title {

        color: white;

        font-size: 16px;

        font-weight: 700;

        margin-bottom: 7px;
    }

    .video-description {

        color: #94a3b8;

        font-size: 13px;

        line-height: 1.6;
    }


    /* ================================
       FOOTER
       ================================ */

    .footer {

        text-align: center;

        color: #475569;

        font-size: 11px;

        padding: 40px 0 10px;
    }



    /* ================================
       AUTHENTICATION
       ================================ */

    .auth-card {
        text-align: center;
        background: #101827;
        border: 1px solid #202a3c;
        border-radius: 20px;
        padding: 30px 25px 20px;
        margin-bottom: 18px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    }

    .auth-logo {
        width: 62px;
        height: 62px;
        margin: 0 auto 15px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg,#6366f1,#8b5cf6);
        font-size: 30px;
    }

    .auth-title {
        color: white;
        font-size: 30px;
        font-weight: 850;
    }

    .auth-subtitle {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 7px;
    }

    .auth-welcome {
        color: #cbd5e1;
        font-size: 18px;
        font-weight: 700;
        margin-top: 28px;
    }

    /* ================================
       MOBILE
       ================================ */

    @media (max-width: 768px) {

        .main {
            padding: 20px;
        }

        .page-title {
            font-size: 27px;
        }
    }

    </style>
    """
)


# =========================================================
# HELPER
# =========================================================

def page_header(title, subtitle):

    st.html(
        f"""
        <div class="page-header">

            <div class="page-title">
                {title}
            </div>

            <div class="page-subtitle">
                {subtitle}
            </div>

        </div>
        """
    )


def youtube_search_url(topic):

    query = quote_plus(
        f"{topic} tutorial for beginners"
    )

    return (
        "https://www.youtube.com/results?search_query="
        + query
    )


# =========================================================
# GEMINI ROADMAP
# =========================================================

def create_roadmap():

    name = st.session_state.name
    degree = st.session_state.degree
    branch = st.session_state.branch
    year = st.session_state.year
    career = st.session_state.target_career
    level = st.session_state.skill_level
    hours = st.session_state.learning_hours
    skills = st.session_state.current_skills
    interests = st.session_state.interests
    additional = st.session_state.additional_info

    prompt = f"""
You are an expert AI career mentor.

Create a personalized career roadmap for this student.

STUDENT DETAILS

Name: {name}

Degree: {degree}

Branch: {branch}

Year: {year}

Target Career: {career}

Current Skill Level: {level}

Learning Hours Per Week: {hours}

Current Skills:
{skills}

Interests:
{interests}

Additional Information:
{additional}


Create a practical roadmap that the student can follow
step by step.

Include:

1. CAREER OVERVIEW

Explain the target career in simple language.

2. CURRENT SKILL ASSESSMENT

Explain what the student already knows based on the
information provided.

3. SKILL GAPS

Explain what skills are still required.

4. LEARNING ROADMAP

Divide the learning journey into:

- Foundation
- Core Skills
- Intermediate Skills
- Advanced Skills
- Practice
- Portfolio Development

For every major learning topic explain what the student
should learn.

5. PROJECT ROADMAP

Suggest:

- Beginner projects
- Intermediate projects
- Advanced projects
- One strong final portfolio project

6. CERTIFICATIONS

Suggest useful certifications.

7. INTERNSHIP PREPARATION

Explain how the student can prepare for internships.

8. RESUME PREPARATION

Explain what should be included in the resume.

9. INTERVIEW PREPARATION

Explain technical and HR preparation.

10. JOB PREPARATION

Explain how to prepare for placements and jobs.

11. FINAL ACTION PLAN

Give a simple step-by-step action plan.

IMPORTANT:

- Do not write programming code.
- Do not return JSON.
- Do not use tables.
- Use simple language.
- Give practical actions.
- Do not tell the student to learn everything at once.
- Prioritize the skills according to the target career.
- Make it suitable for a college student.
- Use clear headings and bullet points.

Start directly with:

CAREER OVERVIEW
"""

    if not API_KEY:

        raise Exception(
            "GEMINI_API_KEY was not found in your .env file."
        )

    client = genai.Client(
        api_key=API_KEY
    )

    models_to_try = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
    ]

    last_error = None

    for model_name in models_to_try:

        for attempt in range(3):

            try:

                response = client.models.generate_content(

                    model=model_name,

                    contents=prompt,

                    config=types.GenerateContentConfig(

                        temperature=0.7,

                        max_output_tokens=6000
                    )
                )

                return response.text

            except Exception as e:

                last_error = e

                error_text = str(e)

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                ):

                    if attempt < 2:

                        time.sleep(
                            5 * (attempt + 1)
                        )

                        continue

                    break

                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED"
                    in error_text
                ):

                    raise Exception(
                        "Gemini API quota has been reached. "
                        "Please wait and try again."
                    )

                if (
                    "401" in error_text
                    or "403" in error_text
                ):

                    raise Exception(
                        "Gemini API key is invalid "
                        "or does not have access."
                    )

                raise

    raise Exception(
        "Gemini is currently unavailable. "
        "Please try again after a few minutes."
    )


# =========================================================
# DASHBOARD
# =========================================================

def dashboard():

    if not st.session_state.profile_created:

        page_header(
            "Welcome to CareerPath AI 🎓",
            "Create your profile to build your personalized career roadmap."
        )

        col1, col2 = st.columns(
            [1.5, 1]
        )

        with col1:

            st.html(
                """
                <div class="content-card">

                    <div class="content-card-title">
                        🚀 Build Your Career Step by Step
                    </div>

                    <div class="content-card-text">

                        CareerPath AI helps college students
                        understand what they need to learn
                        for their target career.

                        <br><br>

                        Create your profile and get a
                        personalized roadmap containing
                        skills, projects, learning resources
                        and career preparation.

                    </div>

                </div>
                """
            )

            if st.button(
                "Create My Profile →",
                use_container_width=True
            ):

                st.session_state.page = "Profile"

                st.rerun()

        with col2:

            st.html(
                """
                <div class="content-card">

                    <div class="content-card-title">
                        What you can do
                    </div>

                    <div class="content-card-text">

                        🗺️ Generate a career roadmap
                        <br><br>

                        📚 Learn required skills
                        <br><br>

                        🎥 Find learning videos
                        <br><br>

                        💻 Build projects
                        <br><br>

                        🎯 Prepare for your career

                    </div>

                </div>
                """
            )

        return


    name = st.session_state.name

    page_header(
        f"Welcome back, {name} 👋",
        "Your personalized career learning dashboard."
    )

    c1, c2, c3, c4 = st.columns(4)

    stats = [
        ("🧠", "Skills", "Learn"),
        ("🎥", "Videos", "Watch"),
        ("💻", "Projects", "Build"),
        ("🎯", "Career", "Prepare"),
    ]

    for col, (icon, label, value) in zip(
        [c1, c2, c3, c4],
        stats
    ):

        with col:

            st.html(
                f"""
                <div class="stat-card">

                    <div class="stat-icon">
                        {icon}
                    </div>

                    <div class="stat-number">
                        {value}
                    </div>

                    <div class="stat-label">
                        {label}
                    </div>

                </div>
                """
            )


    st.markdown("### 📚 Continue Learning")

    col1, col2 = st.columns(2)

    with col1:

        st.html(
            """
            <div class="content-card">

                <div class="content-card-title">
                    🗺️ My Career Roadmap
                </div>

                <div class="content-card-text">

                    Follow your personalized roadmap
                    and learn the skills required for
                    your target career.

                </div>

            </div>
            """
        )

        if st.button(
            "Open My Roadmap →",
            use_container_width=True,
            key="dashboard_roadmap"
        ):

            st.session_state.page = "My Roadmap"

            st.rerun()


    with col2:

        st.html(
            """
            <div class="content-card">

                <div class="content-card-title">
                    📚 Learn Skills
                </div>

                <div class="content-card-text">

                    Learn your required skills through topics,
                    examples, practice tasks and progress tracking.
                    You can also open YouTube for extra explanations.

                </div>

            </div>
            """
        )

        if st.button(
            "Continue Learning →",
            use_container_width=True,
            key="dashboard_learning"
        ):

            st.session_state.page = "Learn Skills"

            st.rerun()


# =========================================================
# PROFILE
# =========================================================

def profile_page():

    page_header(
        "Student Profile 👤",
        "Tell us about yourself so AI can create your roadmap."
    )

    with st.form("profile_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Full Name",
                value=st.session_state.name,
                placeholder="Enter your name"
            )

            degree = st.selectbox(
                "Degree",
                [
                    "B.Tech",
                    "B.Sc",
                    "BCA",
                    "B.Com",
                    "MCA",
                    "MBA",
                    "Other"
                ]
            )

            branch = st.text_input(
                "Branch / Specialization",
                value=st.session_state.branch,
                placeholder="Example: AIML"
            )

            year = st.selectbox(
                "Current Year",
                [
                    "1st Year",
                    "2nd Year",
                    "3rd Year",
                    "4th Year"
                ]
            )

            career = st.text_input(
                "Target Career",
                value=st.session_state.target_career,
                placeholder="Example: Data Scientist"
            )

        with col2:

            skill_level = st.selectbox(
                "Current Skill Level",
                [
                    "Beginner",
                    "Intermediate",
                    "Advanced"
                ]
            )

            hours = st.slider(
                "Learning Hours Per Week",
                1,
                40,
                st.session_state.learning_hours
            )

            skills = st.text_area(
                "Current Skills",
                value=st.session_state.current_skills,
                placeholder="Example: Python, SQL, HTML"
            )

            interests = st.text_area(
                "Interests",
                value=st.session_state.interests,
                placeholder="Example: AI, Data Science, Web Development"
            )

        additional = st.text_area(
            "Additional Information",
            value=st.session_state.additional_info,
            placeholder="Anything else you want the AI mentor to know?"
        )

        submitted = st.form_submit_button(
            "Save Profile",
            use_container_width=True
        )


    if submitted:

        if not name or not career:

            st.error(
                "Please enter your name and target career."
            )

            return

        st.session_state.name = name
        st.session_state.degree = degree
        st.session_state.branch = branch
        st.session_state.year = year
        st.session_state.target_career = career
        st.session_state.skill_level = skill_level
        st.session_state.learning_hours = hours
        st.session_state.current_skills = skills
        st.session_state.interests = interests
        st.session_state.additional_info = additional

        st.session_state.profile_created = True

        st.success(
            "Profile saved successfully!"
        )

        st.session_state.page = "Dashboard"

        st.rerun()


# =========================================================
# ROADMAP
# =========================================================

def roadmap_page():

    page_header(
        "My Career Roadmap 🗺️",
        "Your personalized AI-generated learning journey."
    )

    if not st.session_state.profile_created:

        st.info(
            "Create your profile first."
        )

        if st.button(
            "Create Profile →",
            use_container_width=True
        ):

            st.session_state.page = "Profile"

            st.rerun()

        return


    if not st.session_state.roadmap:

        st.html(
            """
            <div class="content-card">

                <div class="content-card-title">
                    🚀 Generate Your Personalized Roadmap
                </div>

                <div class="content-card-text">

                    AI will analyze your current skills,
                    interests and target career and create
                    a step-by-step roadmap.

                </div>

            </div>
            """
        )

        if st.button(
            "✨ Generate My Roadmap",
            use_container_width=True
        ):

            with st.spinner(
                "AI is creating your roadmap..."
            ):

                try:

                    roadmap = create_roadmap()

                    st.session_state.roadmap = roadmap

                    st.success(
                        "Your roadmap has been created!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Something went wrong."
                    )

                    st.warning(
                        str(e)
                    )

        return


    st.html(
        '<div class="roadmap-box">'
    )

    st.markdown(
        st.session_state.roadmap
    )

    st.html(
        "</div>"
    )

    st.download_button(
        "⬇️ Download Roadmap",
        data=st.session_state.roadmap,
        file_name="career_roadmap.txt",
        mime="text/plain",
        use_container_width=True
    )


# =========================================================
# LEARN SKILLS
# =========================================================

def learn_skills():

    page_header(
        "Learn Skills 📚",
        "Learn your career skills step-by-step through topics, examples and practice."
    )

    if not st.session_state.profile_created:
        st.info("Create your profile first.")
        return

    career = st.session_state.target_career

    skill_map = {
        "Data Scientist": [
            "Python", "Statistics", "NumPy", "Pandas",
            "Data Visualization", "SQL", "Machine Learning", "Deep Learning"
        ],
        "Machine Learning Engineer": [
            "Python", "NumPy", "Pandas", "Statistics",
            "Machine Learning", "Deep Learning", "TensorFlow / PyTorch", "MLOps"
        ],
        "AI Engineer": [
            "Python", "Machine Learning", "Deep Learning", "NLP",
            "Generative AI", "LLMs", "RAG", "APIs"
        ],
        "Web Developer": [
            "HTML", "CSS", "JavaScript", "React",
            "Git", "APIs", "Databases", "Deployment"
        ],
        "Software Developer": [
            "Programming", "Data Structures", "Algorithms", "OOP",
            "DBMS", "Git", "APIs", "Problem Solving"
        ]
    }

    skills = skill_map.get(
        career,
        [
            "Python", "Programming Fundamentals", "Data Structures",
            "SQL", "Git", "Projects", "Communication", "Interview Preparation"
        ]
    )

    # Detailed lessons for common skills
    skill_details = {

        "Python": {
            "description": "Learn Python from the basics and build a strong programming foundation.",
            "topics": [
                ("Variables & Data Types",
                 "Learn how variables store values and understand int, float, string and boolean data types.",
                 'name = "Madhavi"\nage = 18\nmarks = 95.5',
                 "Create variables for your name, age, college and marks."),

                ("Input & Output",
                 "Learn how to take information from the user and display results.",
                 'name = input("Enter your name: ")\nprint("Hello", name)',
                 "Create a program that asks for your name and age."),

                ("If-Else",
                 "Learn how programs make decisions using conditions.",
                 'marks = 85\n\nif marks >= 40:\n    print("Pass")\nelse:\n    print("Fail")',
                 "Create a program to check whether a student passed or failed."),

                ("Loops",
                 "Learn how to repeat a block of code using for and while loops.",
                 'for i in range(1, 6):\n    print(i)',
                 "Print numbers from 1 to 10 using a loop."),

                ("Functions",
                 "Learn how to create reusable blocks of code.",
                 'def add(a, b):\n    return a + b\n\nprint(add(10, 20))',
                 "Create a function that calculates student marks percentage."),

                ("Lists, Tuples & Dictionaries",
                 "Learn how to store multiple values and work with collections.",
                 'marks = [85, 90, 78]\nprint(marks[0])',
                 "Create a list containing five subject marks."),

                ("Object-Oriented Programming",
                 "Learn classes, objects, constructors and methods.",
                 'class Student:\n    def __init__(self, name):\n        self.name = name',
                 "Create a Student class with name and marks."),

                ("NumPy & Pandas",
                 "Learn the basic libraries used for numerical computing and data analysis.",
                 'import pandas as pd\n\ndata = {"Name": ["A", "B"], "Marks": [90, 85]}\ndf = pd.DataFrame(data)\nprint(df)',
                 "Create a small student DataFrame using Pandas.")
            ]
        },

        "Statistics": {
            "description": "Learn the statistical concepts required for data science and machine learning.",
            "topics": [
                ("Mean, Median & Mode",
                 "Learn the three basic measures of central tendency.",
                 "Mean = Sum of values / Number of values",
                 "Calculate mean, median and mode for five numbers."),

                ("Probability",
                 "Understand the basic concepts of probability and events.",
                 "Probability = Favorable outcomes / Total outcomes",
                 "Calculate the probability of getting a head when tossing a coin."),

                ("Variance & Standard Deviation",
                 "Learn how data values differ from their average.",
                 "Variance measures spread in the data.",
                 "Calculate the standard deviation of a small dataset."),

                ("Distributions",
                 "Learn how data is distributed and understand common distributions.",
                 "Normal distribution is one of the most commonly used distributions.",
                 "Identify whether a dataset roughly follows a normal distribution."),

                ("Correlation",
                 "Learn how two variables are related to each other.",
                 "Correlation ranges from -1 to +1.",
                 "Find whether study hours and marks are positively correlated."),

                ("Hypothesis Testing",
                 "Learn how statistical tests help make decisions using data.",
                 "H0 = Null Hypothesis\nH1 = Alternative Hypothesis",
                 "Write a simple null and alternative hypothesis.")
            ]
        },

        "NumPy": {
            "description": "Learn NumPy for numerical calculations and array operations.",
            "topics": [
                ("NumPy Arrays", "Learn how to create and work with NumPy arrays.",
                 "import numpy as np\narr = np.array([1, 2, 3])",
                 "Create a NumPy array containing five numbers."),
                ("Array Indexing", "Learn how to access individual elements from an array.",
                 "arr[0]\narr[1]", "Access the first and last elements of an array."),
                ("Array Operations", "Perform mathematical operations on arrays.",
                 "arr = np.array([1, 2, 3])\nprint(arr * 2)",
                 "Multiply every element of an array by 5."),
                ("Matrix Operations", "Learn addition, subtraction and multiplication of matrices.",
                 "A + B\nA - B\nA @ B",
                 "Create two 2×2 matrices and add them."),
                ("Statistics with NumPy", "Calculate mean, minimum, maximum and standard deviation.",
                 "np.mean(arr)\nnp.max(arr)\nnp.min(arr)",
                 "Find the average of five numbers using NumPy.")
            ]
        },

        "Pandas": {
            "description": "Learn Pandas for handling, cleaning and analyzing datasets.",
            "topics": [
                ("Series & DataFrame", "Learn the basic data structures used in Pandas.",
                 "import pandas as pd\n\ndf = pd.DataFrame(data)",
                 "Create a DataFrame containing student information."),
                ("Reading CSV Files", "Learn how to load datasets into Pandas.",
                 "df = pd.read_csv('data.csv')",
                 "Load a CSV dataset using Pandas."),
                ("Selecting Data", "Learn how to select rows and columns from a DataFrame.",
                 "df['Marks']\ndf.iloc[0]",
                 "Select one column and one row from a dataset."),
                ("Filtering Data", "Learn how to filter records based on conditions.",
                 "df[df['Marks'] > 80]",
                 "Display students whose marks are greater than 80."),
                ("Data Cleaning", "Learn how to handle missing and duplicate data.",
                 "df.dropna()\ndf.drop_duplicates()",
                 "Find and remove missing values from a dataset."),
                ("Data Analysis", "Learn grouping, aggregation and basic statistical analysis.",
                 "df['Marks'].mean()",
                 "Find the average marks from a dataset.")
            ]
        },

        "Machine Learning": {
            "description": "Learn the fundamentals of machine learning and build predictive models.",
            "topics": [
                ("Introduction to Machine Learning",
                 "Understand supervised, unsupervised and reinforcement learning.",
                 "Machine Learning = Learning patterns from data",
                 "Give two real-world examples of machine learning."),
                ("Linear Regression", "Learn how to predict continuous values.",
                 "y = mx + c", "Build a simple model to predict house prices."),
                ("Classification", "Learn how models classify data into categories.",
                 "Examples: spam/not spam, pass/fail",
                 "Identify whether a problem is classification or regression."),
                ("Clustering", "Learn how to group similar data points without labelled data.",
                 "K-Means is a popular clustering algorithm.",
                 "Think of a real-world problem where clustering can be used."),
                ("Train & Test Split", "Learn how to divide data for training and evaluation.",
                 "X_train, X_test, y_train, y_test",
                 "Split a dataset into training and testing data."),
                ("Model Evaluation", "Learn accuracy, precision, recall, F1-score and other metrics.",
                 "Accuracy = Correct predictions / Total predictions",
                 "Calculate accuracy from a confusion matrix.")
            ]
        },

        "Deep Learning": {
            "description": "Learn neural networks and the fundamentals of deep learning.",
            "topics": [
                ("Neural Networks", "Understand neurons, layers, weights and biases.",
                 "Input → Hidden Layers → Output",
                 "Draw a simple neural network with an input and output layer."),
                ("Activation Functions", "Learn ReLU, Sigmoid and other activation functions.",
                 "ReLU(x) = max(0, x)",
                 "Explain why activation functions are required."),
                ("Forward Propagation", "Learn how input data moves through a neural network.",
                 "Input → Weights → Activation → Output",
                 "Explain forward propagation in your own words."),
                ("Backpropagation", "Learn how neural networks update their weights using errors.",
                 "Prediction → Error → Weight Update",
                 "Explain why backpropagation is important."),
                ("CNN", "Learn how convolutional neural networks process images.",
                 "Image → Convolution → Pooling → Classification",
                 "Identify one application of CNNs."),
                ("RNN", "Learn how neural networks can work with sequential data.",
                 "RNNs are useful for sequence-based problems.",
                 "Give one example where sequential data is used.")
            ]
        },

        "SQL": {
            "description": "Learn SQL to store, retrieve and analyze data from databases.",
            "topics": [
                ("SELECT", "Learn how to retrieve data from database tables.",
                 "SELECT * FROM students;", "Display all records from a student table."),
                ("WHERE", "Filter records using conditions.",
                 "SELECT * FROM students WHERE marks > 80;",
                 "Find students who scored more than 80."),
                ("ORDER BY", "Sort query results.",
                 "SELECT * FROM students ORDER BY marks DESC;",
                 "Display students from highest to lowest marks."),
                ("GROUP BY", "Group records and perform aggregate calculations.",
                 "SELECT department, COUNT(*)\nFROM students\nGROUP BY department;",
                 "Count students in each department."),
                ("JOINS", "Combine data from multiple tables.",
                 "SELECT *\nFROM students\nJOIN departments\nON students.dept_id = departments.id;",
                 "Join two related tables.")
            ]
        },

        "HTML": {
            "description": "Learn HTML to create the structure of web pages.",
            "topics": [
                ("HTML Basics", "Learn elements, tags and the basic structure of an HTML page.",
                 "<h1>Hello World</h1>", "Create a simple webpage with a heading."),
                ("Links & Images", "Learn how to add links and images.",
                 '<a href="https://example.com">Visit</a>',
                 "Create a webpage containing an image and a link."),
                ("Forms", "Learn input fields, buttons and forms.",
                 '<input type="text">\n<button>Submit</button>',
                 "Create a simple student registration form.")
            ]
        },

        "CSS": {
            "description": "Learn CSS to style and design attractive web pages.",
            "topics": [
                ("Selectors", "Learn how to select HTML elements for styling.",
                 "p { font-size: 20px; }", "Change the font size of a paragraph."),
                ("Colors & Fonts", "Learn how to change colors, fonts and text appearance.",
                 "color: blue;\nfont-size: 20px;",
                 "Design a heading with your preferred font and color."),
                ("Flexbox", "Learn how to arrange elements using Flexbox.",
                 "display: flex;", "Create a horizontal navigation bar.")
            ]
        },

        "JavaScript": {
            "description": "Learn JavaScript to add logic and interaction to websites.",
            "topics": [
                ("Variables", "Learn let, const and basic JavaScript data types.",
                 "let name = 'Madhavi';", "Create variables for your name and age."),
                ("Functions", "Learn how to create reusable JavaScript functions.",
                 "function add(a, b) {\n  return a + b;\n}",
                 "Create a function that calculates two numbers."),
                ("DOM", "Learn how JavaScript interacts with HTML elements.",
                 "document.getElementById('title')",
                 "Change the text of an HTML element using JavaScript.")
            ]
        },

        "Data Structures": {
            "description": "Learn important data structures used in programming and technical interviews.",
            "topics": [
                ("Arrays & Lists", "Learn how to store and access multiple values.",
                 "arr = [10, 20, 30]", "Find the largest element in a list."),
                ("Stack", "Learn LIFO data structure and its applications.",
                 "Push → Pop", "Implement a stack using a Python list."),
                ("Queue", "Learn FIFO data structure and its applications.",
                 "Enqueue → Dequeue", "Implement a queue."),
                ("Linked List", "Learn nodes and links in a linked list.",
                 "Node → Node → Node", "Create a simple singly linked list."),
                ("Trees", "Learn hierarchical data structures.",
                 "Root → Children", "Draw a binary tree with five nodes."),
                ("Graphs", "Learn vertices, edges and graph traversal.",
                 "DFS / BFS", "Draw a graph containing five vertices.")
            ]
        },

        "OOP": {
            "description": "Learn object-oriented programming concepts used in software development.",
            "topics": [
                ("Classes & Objects", "Learn how classes define objects and their properties.",
                 "class Student:\n    pass", "Create a Student class."),
                ("Constructor", "Learn how __init__ initializes objects.",
                 "def __init__(self, name):\n    self.name = name",
                 "Create a class with a constructor."),
                ("Inheritance", "Learn how one class can inherit from another.",
                 "class Child(Parent):\n    pass", "Create a parent and child class."),
                ("Polymorphism", "Learn how the same method can behave differently.",
                 "Different classes can implement the same method.",
                 "Create two classes with the same method name.")
            ]
        }
    }

    selected_skill = st.selectbox(
        "Choose a skill to start learning",
        skills,
        key="selected_learning_skill"
    )

    # Generic lessons for skills that do not yet have custom content
    default_topics = [
        ("Fundamentals",
         f"Learn the basic concepts and terminology of {career} through {selected_skill}.",
         f"# Start learning {selected_skill}",
         f"Write down five important concepts of {selected_skill}."),
        ("Core Concepts",
         f"Understand the main concepts used in {selected_skill}.",
         f"# Core concepts of {selected_skill}",
         f"Explain two important concepts of {selected_skill} in your own words."),
        ("Practical Usage",
         f"Learn how {selected_skill} is used in real-world applications.",
         f"# Practice {selected_skill}",
         f"Find one real-world application of {selected_skill}."),
        ("Mini Project",
         f"Apply what you learned by building a small project using {selected_skill}.",
         f"# Your {selected_skill} project",
         f"Build a small beginner project using {selected_skill}.")
    ]

    details = skill_details.get(
        selected_skill,
        {
            "description": f"Build a strong foundation in {selected_skill}.",
            "topics": default_topics
        }
    )

    st.html(
        f"""
        <div class="content-card">
            <div class="content-card-title">
                🎯 {career}
            </div>
            <div class="content-card-text">
                You are learning <b style="color:white;">{selected_skill}</b>.
                Complete each topic, practice it and mark it as completed.
            </div>
        </div>
        """
    )

    st.html(
        f"""
        <div class="content-card">
            <div class="content-card-title">
                📘 {selected_skill}
            </div>
            <div class="content-card-text">
                {details["description"]}
            </div>
        </div>
        """
    )

    progress_key = f"completed_{selected_skill}"

    if progress_key not in st.session_state:
        st.session_state[progress_key] = []

    completed_topics = st.session_state[progress_key]
    total_topics = len(details["topics"])
    completed_count = len(completed_topics)
    progress = completed_count / total_topics if total_topics else 0

    st.progress(progress)
    st.markdown(
        f"**Progress:** {completed_count} / {total_topics} topics completed"
    )

    st.markdown("---")

    for index, (topic_name, explanation, example, practice) in enumerate(
        details["topics"], 1
    ):

        is_completed = topic_name in completed_topics

        if is_completed:
            topic_label = f"✅ Topic {index}: {topic_name} — Completed"
        else:
            topic_label = f"🔵 Topic {index}: {topic_name}"

        # Click the topic to open its full explanation
        with st.expander(topic_label, expanded=False):

            st.markdown("### 📖 Explanation")
            st.write(explanation)

            st.markdown("### 💡 Example")
            st.code(example)

            st.markdown("### 🧠 Practice")
            st.html(
                f"""
                <div style="
                    background:#101827;
                    border:1px solid #263244;
                    border-left:4px solid #6366f1;
                    border-radius:12px;
                    padding:16px;
                    margin:8px 0 16px 0;
                ">
                    <div style="color:#cbd5e1;line-height:1.6;">
                        {practice}
                    </div>
                </div>
                """
            )

            col1, col2 = st.columns(2)

            with col1:
                if not is_completed:
                    if st.button(
                        "✅ Mark as Completed",
                        key=f"complete_{selected_skill}_{index}",
                        use_container_width=True
                    ):
                        st.session_state[progress_key].append(topic_name)
                        st.rerun()
                else:
                    st.success("Topic completed!")

            with col2:
                st.link_button(
                    "🎥 Learn on YouTube",
                    youtube_search_url(f"{selected_skill} {topic_name}"),
                    use_container_width=True
                )

            st.info(
                "💡 Read the explanation, check the example, try the practice, "
                "and then mark this topic as completed."
            )


    if progress == 1:
        st.success(f"🎉 Amazing! You completed all {selected_skill} topics!")
        st.balloons()
    elif progress > 0:
        st.info(f"💪 Great progress! Keep learning {selected_skill}.")


# =========================================================
# PROFILE SUMMARY
# =========================================================

def profile_summary():

    if not st.session_state.profile_created:

        return

    st.html(
        f"""
        <div class="sidebar-profile">

            <div class="sidebar-profile-name">
                👤 {st.session_state.name}
            </div>

            <div class="sidebar-profile-career">
                @ {st.session_state.username}
            </div>

            <div class="sidebar-profile-career">
                🎯 {st.session_state.target_career}
            </div>

        </div>
        """
    )


# =========================================================
# AUTHENTICATION GATE
# =========================================================

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

if not st.session_state.logged_in:
    if st.session_state.auth_page == "register":
        registration_page()
    else:
        login_page()
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.html(
        """
        <div class="sidebar-logo">

            <div class="sidebar-logo-icon">
                🎓
            </div>

            <div>

                <div class="sidebar-logo-title">
                    CareerPath
                </div>

                <div class="sidebar-logo-subtitle">
                    AI Career Learning Platform
                </div>

            </div>

        </div>
        """
    )


    st.html(
        '<div class="sidebar-section">MAIN</div>'
    )


    # ONLY THESE MAIN NAVIGATION ITEMS
    # NO CAREER BUILDING SECTION

    navigation = [

        ("🏠", "Dashboard"),

        ("🗺️", "My Roadmap"),

        ("📚", "Learn Skills"),


    ]


    for icon, page_name in navigation:

        if st.button(
            f"{icon}  {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True
        ):

            st.session_state.page = page_name

            st.rerun()


    st.html(
        '<div class="sidebar-section">ACCOUNT</div>'
    )


    if st.button(
        "👤  Profile",
        key="nav_profile",
        use_container_width=True
    ):

        st.session_state.page = "Profile"

        st.rerun()

    if st.button(
        "🚪  Logout",
        key="nav_logout",
        use_container_width=True
    ):
        for key in ["logged_in", "user_id", "username"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        st.session_state.profile_created = False
        st.session_state.roadmap = ""
        st.rerun()


    profile_summary()


# =========================================================
# PAGE ROUTER
# =========================================================

page = st.session_state.page


if page == "Dashboard":

    dashboard()


elif page == "My Roadmap":

    roadmap_page()


elif page == "Learn Skills":

    learn_skills()


elif page == "Profile":

    profile_page()


# =========================================================
# FOOTER
# =========================================================

st.html(
    """
    <div class="footer">

        CareerPath AI • Student Career Learning Platform

    </div>
    """
)