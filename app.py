import streamlit as st
import pdfplumber
import sqlite3

# =========================
# DATABASE SETUP
# =========================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    password TEXT
)
""")

conn.commit()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="💼",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(
        135deg,
        #020617,
        #0f172a,
        #111827,
        #1e293b
    );
    color: white;
}

/* TITLE */
.main-title {
    text-align: center;
    font-size: 60px;
    font-weight: bold;
    color: #38bdf8;
    margin-bottom: 10px;
}

/* SUBTITLE */
.sub-title {
    text-align: center;
    font-size: 22px;
    color: #cbd5e1;
    margin-bottom: 30px;
}

/* GLASS BOX */
.glass-box {
    background: rgba(255,255,255,0.08);
    padding: 30px;
    border-radius: 20px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin-top: 20px;
}

/* LOGIN BOX */
.login-box {
    background: rgba(255,255,255,0.08);
    padding: 40px;
    border-radius: 25px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    width: 60%;
    margin: auto;
    margin-top: 40px;
}

/* SECTION TITLE */
.section-title {
    color: #38bdf8;
    font-size: 30px;
    margin-top: 20px;
    margin-bottom: 15px;
    font-weight: bold;
}

/* SKILL BOX */
.skill-box {
    background: linear-gradient(to right, #16a34a, #22c55e);
    padding: 14px;
    border-radius: 12px;
    margin-bottom: 10px;
    color: white;
    font-weight: bold;
    font-size: 18px;
}

/* INFO BOX */
.info-box {
    background: rgba(255,255,255,0.05);
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 15px;
    border-left: 5px solid #38bdf8;
}

/* SCORE BOX */
.score-box {
    background: linear-gradient(to right, #2563eb, #1d4ed8);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    color: white;
    margin-top: 20px;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    border: 2px dashed #38bdf8;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(to right, #2563eb, #38bdf8);
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
    font-size: 18px;
    font-weight: bold;
    border: none;
}

/* INPUT */
.stTextInput>div>div>input {
    background-color: rgba(255,255,255,0.05);
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# MENU
# =========================
menu = ["Login", "Signup"]

choice = st.sidebar.selectbox("Menu", menu)

# =========================
# SIGNUP
# =========================
if choice == "Signup":

    st.markdown(
        '<h1 class="main-title">Create Account</h1>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type="password")

    if st.button("Signup"):

        c.execute("SELECT * FROM users WHERE username=?", (new_user,))
        data = c.fetchone()

        if data:
            st.error("Username already exists")

        else:
            c.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (new_user, new_password)
            )
            conn.commit()

            st.success("Account Created Successfully ✅")
            st.info("Go to Login Page")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# LOGIN
# =========================
elif choice == "Login":

    if not st.session_state.logged_in:

        st.markdown(
            '<h1 class="main-title">💼 AI Resume Analyzer</h1>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<p class="sub-title">Smart Resume Analysis System</p>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )

            data = c.fetchone()

            if data:
                st.session_state.logged_in = True
                st.success("Login Successful ✅")
                st.rerun()

            else:
                st.error("Invalid Username or Password ❌")

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # MAIN APP
    # =========================
    else:

        st.markdown(
            '<h1 class="main-title">💼 AI Resume Analyzer</h1>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<p class="sub-title">Upload Resume & Get AI Analysis</p>',
            unsafe_allow_html=True
        )

        # LOGOUT
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        # FILE UPLOAD
        uploaded_file = st.file_uploader(
            "📄 Upload Your Resume",
            type=["pdf"]
        )

        if uploaded_file is not None:

            text = ""

            with pdfplumber.open(uploaded_file) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text

            st.markdown('<div class="glass-box">', unsafe_allow_html=True)

            # =========================
            # NAME
            # =========================
            st.markdown(
                '<div class="section-title">👤 Candidate Name</div>',
                unsafe_allow_html=True
            )

            lines = text.split("\n")

            candidate_name = lines[0]

            st.markdown(
                f'<div class="info-box">{candidate_name}</div>',
                unsafe_allow_html=True
            )

            # =========================
            # SKILLS
            # =========================
            st.markdown(
                '<div class="section-title">🚀 Skills Found</div>',
                unsafe_allow_html=True
            )

            skills = [
                "Python",
                "Java",
                "C++",
                "SQL",
                "JavaScript",
                "React",
                "Node.js",
                "Cybersecurity",
                "Machine Learning",
                "AI",
                "HTML",
                "CSS",
                "MongoDB",
                "Git",
                "AWS"
            ]

            found_skills = []

            for skill in skills:
                if skill.lower() in text.lower():
                    found_skills.append(skill)

            if found_skills:

                for skill in found_skills:

                    st.markdown(
                        f'<div class="skill-box">{skill}</div>',
                        unsafe_allow_html=True
                    )

            else:
                st.warning("No Skills Found")

            # =========================
            # EXPERIENCE DETAILS
            # =========================
            st.markdown(
                '<div class="section-title">💼 Experience</div>',
                unsafe_allow_html=True
            )

            experience_keywords = [
                "intern",
                "developer",
                "experience",
                "worked",
                "company",
                "software engineer"
            ]

            experience_found = []

            for word in experience_keywords:
                if word.lower() in text.lower():
                    experience_found.append(word)

            if experience_found:

                st.markdown(
                    f'''
                    <div class="info-box">
                    Experience Related Details:<br><br>
                    {" , ".join(experience_found)}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

            else:
                st.warning("No Experience Found")

            # =========================
            # ATS SCORE
            # =========================
            score = min(len(found_skills) * 10, 100)

            st.markdown(
                f'<div class="score-box">ATS Resume Score: {score}/100</div>',
                unsafe_allow_html=True
            )

            st.progress(score)

            # =========================
            # EDUCATION DETAILS
            # =========================
            st.markdown(
                '<div class="section-title">🎓 Education</div>',
                unsafe_allow_html=True
            )

            education_keywords = [
                "B.Tech",
                "Bachelor",
                "Master",
                "University",
                "College",
                "Computer Science"
            ]

            education_found = []

            for edu in education_keywords:
                if edu.lower() in text.lower():
                    education_found.append(edu)

            if education_found:

                st.markdown(
                    f'''
                    <div class="info-box">
                    Education Details:<br><br>
                    {" , ".join(education_found)}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

            else:
                st.warning("No Education Details Found")

            # =========================
            # CERTIFICATES DETAILS
            # =========================
            st.markdown(
                '<div class="section-title">📜 Certificates</div>',
                unsafe_allow_html=True
            )

            certificate_keywords = [
                "certificate",
                "certification",
                "google",
                "aws",
                "coursera",
                "udemy"
            ]

            certificate_found = []

            for cert in certificate_keywords:
                if cert.lower() in text.lower():
                    certificate_found.append(cert)

            if certificate_found:

                st.markdown(
                    f'''
                    <div class="info-box">
                    Certificates Found:<br><br>
                    {" , ".join(certificate_found)}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

            else:
                st.warning("No Certificates Found")

            # =========================
            # PROJECT DETAILS
            # =========================
            st.markdown(
                '<div class="section-title">🛠 Projects</div>',
                unsafe_allow_html=True
            )

            project_keywords = [
                "project",
                "ai",
                "machine learning",
                "web app",
                "resume analyzer",
                "chatbot"
            ]

            project_found = []

            for project in project_keywords:
                if project.lower() in text.lower():
                    project_found.append(project)

            if project_found:

                st.markdown(
                    f'''
                    <div class="info-box">
                    Project Related Details:<br><br>
                    {" , ".join(project_found)}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

            else:
                st.warning("No Projects Found")

            # =========================
            # JOB ROLE PREDICTION
            # =========================
            st.markdown(
                '<div class="section-title">💼 Predicted Job Role</div>',
                unsafe_allow_html=True
            )

            if "react" in text.lower():
                st.success("Frontend Developer")

            elif "python" in text.lower():
                st.success("Python Developer")

            elif "machine learning" in text.lower():
                st.success("Machine Learning Engineer")

            elif "cybersecurity" in text.lower():
                st.success("Cybersecurity Analyst")

            else:
                st.success("Software Engineer")

            # =========================
            # SHORT SUMMARY
            # =========================
            st.markdown(
                '<div class="section-title">📝 Resume Summary</div>',
                unsafe_allow_html=True
            )

            summary = f"""
            This candidate has skills in {", ".join(found_skills[:3])}.
            The resume includes education, projects, and technical knowledge.
            Predicted suitable role is based on the detected technical skills.
            """

            st.markdown(
                f'''
                <div class="info-box">
                {summary}
                </div>
                ''',
                unsafe_allow_html=True
            )

            st.markdown('</div>', unsafe_allow_html=True)