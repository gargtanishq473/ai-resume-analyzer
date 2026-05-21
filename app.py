import streamlit as st
import pdfplumber
import sqlite3

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="💼",
    layout="wide"
)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    email TEXT,
    password TEXT
)
""")
conn.commit()

# =========================
# HELPER FUNCTIONS
# =========================
def get_section(text, start_keywords, end_keywords):

    text_lower = text.lower()
    start_index = -1

    for keyword in start_keywords:

        index = text_lower.find(keyword.lower())

        if index != -1:
            start_index = index
            break

    if start_index == -1:
        return ""

    end_index = len(text)

    for keyword in end_keywords:

        index = text_lower.find(keyword.lower(), start_index + 1)

        if index != -1:
            end_index = min(end_index, index)

    return text[start_index:end_index].strip()


def clean_lines(section_text):

    lines = section_text.split("\n")
    cleaned = []

    for line in lines:

        line = line.strip()

        if line and len(line) > 3:
            cleaned.append(line)

    return cleaned[:8]


# =========================
# SESSION STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# =========================
# THEME
# =========================
dark_bg = """
background:
radial-gradient(circle at top left, rgba(56,189,248,0.25), transparent 35%),
radial-gradient(circle at bottom right, rgba(168,85,247,0.22), transparent 35%),
linear-gradient(135deg, #020617, #0f172a, #111827);
color: white;
"""

light_bg = """
background:
linear-gradient(135deg, #f8fafc, #e0f2fe, #f1f5f9);
color: #0f172a;
"""

bg = dark_bg if st.session_state.theme == "dark" else light_bg

# =========================
# CSS
# =========================
st.markdown(f"""
<style>

.stApp {{
    {bg}
}}

.hero {{
    text-align: center;
    padding: 110px 20px 70px 20px;
}}

.hero-title {{
    font-size: 65px;
    font-weight: 900;
    color: #22d3ee;
    text-shadow: 0 0 25px rgba(34,211,238,0.7);
}}

.hero-sub {{
    font-size: 22px;
    color: #cbd5e1;
    margin-top: 15px;
}}

.card {{
    background: rgba(255,255,255,0.09);
    padding: 30px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 10px 35px rgba(0,0,0,0.35);
    backdrop-filter: blur(14px);
    margin-top: 25px;
}}

.login-card {{
    background: rgba(255,255,255,0.09);
    padding: 35px;
    border-radius: 22px;
    width: 60%;
    margin: auto;
    margin-top: 50px;
    border: 1px solid rgba(34,211,238,0.35);
    box-shadow: 0 0 35px rgba(34,211,238,0.18);
}}

.section-title {{
    color: #22d3ee;
    font-size: 30px;
    font-weight: 800;
    margin-top: 25px;
    margin-bottom: 15px;
}}

.skill-box {{
    background: linear-gradient(90deg, #06b6d4, #8b5cf6);
    color: white;
    padding: 13px;
    border-radius: 12px;
    margin: 8px 0;
    font-weight: 700;
}}

.info-box {{
    background: rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 14px;
    border-left: 5px solid #22d3ee;
    margin-bottom: 15px;
}}

.score-box {{
    background: linear-gradient(90deg, #2563eb, #06b6d4);
    padding: 22px;
    border-radius: 16px;
    text-align: center;
    font-size: 28px;
    font-weight: 900;
    color: white;
    margin: 20px 0;
}}

.stButton>button {{
    background: linear-gradient(90deg, #06b6d4, #8b5cf6);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-weight: 800;
}}

[data-testid="stFileUploader"] {{
    background: rgba(255,255,255,0.08);
    border: 2px dashed #22d3ee;
    border-radius: 18px;
    padding: 20px;
}}

</style>
""", unsafe_allow_html=True)

# =========================
# NAVBAR
# =========================
col1, col2, col3, col4, col5 = st.columns([4, 1, 1, 1, 1])

with col1:
    st.markdown("## 💼 AI RESUME ANALYZER")

with col2:
    if st.button("Home"):
        st.session_state.page = "Home"

with col3:
    if st.button("About"):
        st.session_state.page = "About"

with col4:
    if st.button("Help"):
        st.session_state.page = "Help"

with col5:
    if st.button("☀️/🌙"):
        st.session_state.theme = (
            "light" if st.session_state.theme == "dark" else "dark"
        )
        st.rerun()

# =========================
# HOME PAGE
# =========================
if st.session_state.page == "Home":

    st.markdown("""
    <div class="hero">
        <div class="hero-title">AI RESUME ANALYZER</div>
        <div class="hero-sub">
            Analyze resume, calculate ATS score and improve your resume.
        </div>
    </div>
    """, unsafe_allow_html=True)

    center = st.columns([2,1,2])

    with center[1]:

        if st.button("ACCESS ANALYZER"):
            st.session_state.page = "Login"
            st.rerun()

# =========================
# ABOUT PAGE
# =========================
elif st.session_state.page == "About":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">About Developer</div>',
        unsafe_allow_html=True
    )

    st.write("Name: Tanishq Garg")
    st.write("Field: Computer Science & Artificial Intelligence")

    st.markdown(
        '<div class="section-title">About Website</div>',
        unsafe_allow_html=True
    )

    st.write("""
    This website analyzes resumes using AI techniques.
    It detects skills, education, certificates, projects,
    experience and gives ATS score with improvement tips.
    """)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HELP PAGE
# =========================
elif st.session_state.page == "Help":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">How This Website Works</div>',
        unsafe_allow_html=True
    )

    st.write("1. Create account or login.")
    st.write("2. Upload your resume PDF.")
    st.write("3. Website reads resume text.")
    st.write("4. AI detects skills and sections.")
    st.write("5. ATS score and improvement tips are generated.")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# LOGIN PAGE
# =========================
elif st.session_state.page == "Login":

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    option = st.radio("Choose Option", ["Login", "Signup"])

    if option == "Signup":

        st.subheader("Create Account")

        new_user = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")

        if st.button("Signup"):

            c.execute(
                "SELECT * FROM users WHERE email=?",
                (new_email,)
            )

            data = c.fetchone()

            if data:
                st.error("Email already registered")

            else:

                c.execute(
                    "INSERT INTO users(username,email,password) VALUES(?,?,?)",
                    (new_user, new_email, new_password)
                )

                conn.commit()

                st.success("Account Created Successfully")

    else:

        st.subheader("Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            c.execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (email, password)
            )

            data = c.fetchone()

            if data:

                st.session_state.logged_in = True
                st.session_state.page = "Analyzer"

                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Email or Password")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ANALYZER PAGE
# =========================
elif st.session_state.page == "Analyzer":

    if not st.session_state.logged_in:

        st.warning("Please Login First")
        st.session_state.page = "Login"
        st.rerun()

    st.markdown("## Upload Resume & Get AI Analysis")

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.page = "Home"
        st.rerun()

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
                    text += page_text + "\n"

        st.markdown('<div class="card">', unsafe_allow_html=True)

        lines = text.split("\n")

        candidate_name = lines[0] if lines else "Candidate"

        # =========================
        # NAME
        # =========================
        st.markdown(
            '<div class="section-title">👤 Candidate Name</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="info-box">{candidate_name}</div>',
            unsafe_allow_html=True
        )

        # =========================
        # SKILLS
        # =========================
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
            "AWS",
            "Data Science"
        ]

        found_skills = []

        for skill in skills:

            if skill.lower() in text.lower():
                found_skills.append(skill)

        st.markdown(
            '<div class="section-title">🚀 Skills Found</div>',
            unsafe_allow_html=True
        )

        if found_skills:

            for skill in found_skills:

                st.markdown(
                    f'<div class="skill-box">{skill}</div>',
                    unsafe_allow_html=True
                )

        else:
            st.warning("No Skills Found")

        # =========================
        # EXPERIENCE
        # =========================
        st.markdown(
            '<div class="section-title">💼 Experience</div>',
            unsafe_allow_html=True
        )

        experience_text = get_section(
            text,
            ["experience", "work experience", "internship"],
            ["education", "skills", "projects", "certificates"]
        )

        experience_lines = clean_lines(experience_text)

        if experience_lines:

            st.markdown("<div class='info-box'>", unsafe_allow_html=True)

            for line in experience_lines:

                if line.lower() not in [
                    "experience",
                    "work experience"
                ]:
                    st.write("•", line)

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.warning("No Proper Experience Details Found")

        # =========================
        # REALISTIC ATS SCORE
        # =========================
        score = 35

        if len(found_skills) >= 8:
            score += 20

        elif len(found_skills) >= 5:
            score += 15

        elif len(found_skills) >= 3:
            score += 10

        else:
            score += 5

        # PROJECTS
        project_text = get_section(
            text,
            ["projects", "project"],
            ["certificates", "education", "skills", "experience"]
        )

        project_lines = clean_lines(project_text)

        if project_lines:
            score += 15
        else:
            score -= 10

        # EXPERIENCE
        if experience_lines:
            score += 10
        else:
            score -= 5

        # EDUCATION
        education_text = get_section(
            text,
            ["education", "academic background"],
            ["skills", "projects", "certificates", "experience"]
        )

        education_lines = clean_lines(education_text)

        if education_lines:
            score += 10

        # CERTIFICATES
        certificate_text = get_section(
            text,
            ["certificates", "certifications", "certificate"],
            ["projects", "skills", "education", "experience"]
        )

        certificate_lines = clean_lines(certificate_text)

        if certificate_lines:
            score += 5

        # SHORT RESUME PENALTY
        if len(text.split()) < 250:
            score -= 15

        # SUMMARY PENALTY
        if "summary" not in text.lower():
            score -= 5

        # LIMIT
        if score > 92:
            score = 92

        if score < 35:
            score = 35

        st.markdown(
            f'<div class="score-box">ATS Resume Score: {score}/100</div>',
            unsafe_allow_html=True
        )

        st.progress(score)

        # =========================
        # EDUCATION
        # =========================
        st.markdown(
            '<div class="section-title">🎓 Education</div>',
            unsafe_allow_html=True
        )

        if education_lines:

            st.markdown("<div class='info-box'>", unsafe_allow_html=True)

            for line in education_lines:

                if line.lower() not in ["education"]:
                    st.write("•", line)

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.warning("No Proper Education Details Found")

        # =========================
        # CERTIFICATES
        # =========================
        st.markdown(
            '<div class="section-title">📜 Certificates</div>',
            unsafe_allow_html=True
        )

        if certificate_lines:

            st.markdown("<div class='info-box'>", unsafe_allow_html=True)

            for line in certificate_lines:

                if line.lower() not in [
                    "certificate",
                    "certificates",
                    "certification"
                ]:
                    st.write("•", line)

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.warning("No Proper Certificates Found")

        # =========================
        # PROJECTS
        # =========================
        st.markdown(
            '<div class="section-title">🛠 Projects</div>',
            unsafe_allow_html=True
        )

        if project_lines:

            st.markdown("<div class='info-box'>", unsafe_allow_html=True)

            for line in project_lines:

                if line.lower() not in ["projects", "project"]:
                    st.write("•", line)

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.warning("No Proper Projects Found")

        # =========================
        # JOB ROLE
        # =========================
        st.markdown(
            '<div class="section-title">💼 Predicted Job Role</div>',
            unsafe_allow_html=True
        )

        if "cybersecurity" in text.lower():
            role = "Cybersecurity Analyst"

        elif "react" in text.lower():
            role = "Frontend Developer"

        elif "machine learning" in text.lower():
            role = "Machine Learning Engineer"

        elif "python" in text.lower():
            role = "Python Developer"

        elif "java" in text.lower():
            role = "Java Developer"

        else:
            role = "Software Engineer"

        st.success(role)

        # =========================
        # HOW TO IMPROVE RESUME
        # =========================
        st.markdown(
            '<div class="section-title">🚀 How To Improve Your Resume</div>',
            unsafe_allow_html=True
        )

        improvement_text = ""

        # Skills
        if len(found_skills) < 5:

            improvement_text += """
            🔹 Add more technical skills related to your target job role.
            Add technologies like React, SQL, Machine Learning,
            AWS, Data Science, etc.

            """

        # Projects
        if not project_lines:

            improvement_text += """
            🔹 Add at least 2 strong projects with:
            • Project Name
            • Technologies Used
            • Features
            • Problem Solved

            """

        # Experience
        if not experience_lines:

            improvement_text += """
            🔹 Add internship, freelance work or practical experience.

            """

        # Resume Length
        if len(text.split()) < 250:

            improvement_text += """
            🔹 Resume content is too short.
            Explain projects, achievements and technical work properly.

            """

        # Certificates
        if not certificate_lines:

            improvement_text += """
            🔹 Add certificates like:
            • Google Cybersecurity
            • AWS Cloud
            • IBM AI
            • Cisco Networking

            """

        # ATS
        if score < 70:

            improvement_text += """
            🔹 ATS score is below average.
            Add professional keywords and improve formatting.

            """

        # Strong Resume
        if improvement_text == "":

            improvement_text = """
            ✅ Resume looks professional.

            To make it even stronger:
            • Add measurable achievements
            • Add GitHub links
            • Add portfolio website
            • Add leadership experience

            """

        st.markdown(
            f'<div class="info-box">{improvement_text}</div>',
            unsafe_allow_html=True
        )

        # =========================
        # SHORT SUMMARY
        # =========================
        st.markdown(
            '<div class="section-title">📝 Short Resume Summary</div>',
            unsafe_allow_html=True
        )

        top_skills = (
            ", ".join(found_skills[:5])
            if found_skills
            else "technical skills"
        )

        summary = f"""
        {candidate_name} has a technical profile with skills in
        {top_skills}.

        The resume achieved an ATS score of {score}/100
        and is suitable for the role of {role}.

        The resume can be improved further by adding
        measurable achievements, strong projects,
        industry certificates and job-specific keywords.
        """

        st.markdown(
            f"<div class='info-box'>{summary}</div>",
            unsafe_allow_html=True
        )

        st.markdown('</div>', unsafe_allow_html=True)