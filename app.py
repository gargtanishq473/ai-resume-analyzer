import streamlit as st
import pdfplumber
import sqlite3
import hashlib

st.set_page_config(page_title="AI Resume Analyzer", page_icon="💼", layout="wide")

# DATABASE
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

# SESSION
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

def hash_password(password):
    salt = "ai_resume_analyzer_secret_salt"
    return hashlib.sha256((password + salt).encode()).hexdigest()

# COOL CSS + ANIMATION + WATERMARK
st.markdown("""
<style>
.stApp{
    background: linear-gradient(-45deg,#020617,#0f172a,#1e1b4b,#312e81);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
    color:white;
    overflow-x:hidden;
}

@keyframes gradientBG{
    0%{background-position:0% 50%;}
    50%{background-position:100% 50%;}
    100%{background-position:0% 50%;}
}

.hero{
    padding:70px;
    border-radius:30px;
    background:rgba(255,255,255,0.08);
    backdrop-filter: blur(15px);
    border:1px solid rgba(255,255,255,0.18);
    box-shadow:0 0 35px rgba(34,211,238,0.25);
    text-align:center;
    animation: fadeIn 1.5s ease, floatAnim 4s ease-in-out infinite;
    margin-top:30px;
}

.hero-title{
    font-size:75px;
    font-weight:900;
    color:#38bdf8;
    text-shadow:0 0 20px rgba(56,189,248,0.8);
    animation: glow 2s infinite alternate;
}

.hero-sub{
    font-size:24px;
    color:#dbeafe;
    margin-top:15px;
}

@keyframes glow{
    from{text-shadow:0 0 10px #38bdf8;}
    to{text-shadow:0 0 35px #06b6d4;}
}

@keyframes fadeIn{
    from{opacity:0; transform:translateY(30px);}
    to{opacity:1; transform:translateY(0);}
}

@keyframes floatAnim{
    0%{transform:translateY(0);}
    50%{transform:translateY(-10px);}
    100%{transform:translateY(0);}
}

.card,.info-box,.login-card{
    background:rgba(255,255,255,0.07);
    backdrop-filter:blur(14px);
    border-radius:24px;
    border:1px solid rgba(255,255,255,0.18);
    box-shadow:0 0 25px rgba(34,211,238,0.15);
    padding:22px;
    animation: fadeIn 1.2s ease;
}

.login-card{
    width:60%;
    margin:auto;
    padding:40px;
}

.section-title{
    font-size:34px;
    font-weight:900;
    color:#38bdf8;
    margin-top:25px;
    margin-bottom:15px;
    text-shadow:0 0 10px rgba(56,189,248,0.7);
}

.skill-box{
    background:linear-gradient(90deg,#06b6d4,#8b5cf6);
    padding:14px;
    border-radius:14px;
    color:white;
    margin:10px 0;
    font-weight:700;
    transition:0.3s;
}

.skill-box:hover{
    transform:scale(1.03);
    box-shadow:0 0 20px rgba(56,189,248,0.5);
}

.score-box{
    background:linear-gradient(90deg,#2563eb,#06b6d4);
    padding:28px;
    border-radius:20px;
    text-align:center;
    font-size:38px;
    font-weight:900;
    color:white;
    box-shadow:0 0 25px rgba(37,99,235,0.4);
}

.stButton>button{
    background:linear-gradient(90deg,#06b6d4,#8b5cf6);
    color:white;
    border:none;
    border-radius:14px;
    padding:12px 24px;
    font-weight:800;
    transition:0.3s;
}

.stButton>button:hover{
    transform:scale(1.08);
    box-shadow:0 0 20px rgba(56,189,248,0.6);
}

.watermark{
    position:fixed;
    bottom:20px;
    right:25px;
    color:rgba(255,255,255,0.22);
    font-size:18px;
    font-weight:700;
    z-index:9999;
    letter-spacing:1px;
}

@media(max-width:768px){
    .hero-title{font-size:42px;}
    .hero-sub{font-size:18px;}
    .login-card{width:95%; padding:20px;}
    .section-title{font-size:26px;}
}
</style>
<div class="watermark">Created by Tanishq Garg</div>
""", unsafe_allow_html=True)

# FUNCTIONS
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

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
    return [line.strip() for line in section_text.split("\n") if line.strip() and len(line.strip()) > 3][:8]

def make_report_text(name, score, role, skills, rank, tips):
    return f"""
AI Resume Analyzer Report

Candidate Name: {name}
ATS Score: {score}/100
Resume Rank: {rank}
Predicted Role: {role}

Skills Found:
{", ".join(skills) if skills else "No major skills found"}

Improvement Tips:
{tips}

Generated by AI Resume Analyzer
"""

def get_rank(score):
    if score >= 85:
        return "Advanced"
    elif score >= 65:
        return "Intermediate"
    return "Beginner"

skills = [
    "Python", "Java", "C++", "SQL", "JavaScript", "React",
    "Node.js", "Cybersecurity", "Machine Learning", "AI",
    "HTML", "CSS", "MongoDB", "AWS", "Flask", "Django"
]

question_bank = {
    "Python": {
        "Beginner": ["What is Python?", "What are lists and tuples?", "What is a function?"],
        "Intermediate": ["Explain OOP in Python.", "What is exception handling?", "What are decorators?"],
        "Advanced": ["Explain generators.", "Explain multithreading vs multiprocessing.", "How does memory management work in Python?"]
    },
    "SQL": {
        "Beginner": ["What is SQL?", "What is a primary key?", "What is SELECT query?"],
        "Intermediate": ["Explain joins.", "What is normalization?", "Difference between WHERE and HAVING?"],
        "Advanced": ["Explain indexing.", "What is query optimization?", "Explain ACID properties."]
    },
    "React": {
        "Beginner": ["What is React?", "What are components?", "What is JSX?"],
        "Intermediate": ["Difference between props and state?", "What is useState?", "Explain useEffect."],
        "Advanced": ["Explain React lifecycle.", "What is memoization?", "How to optimize React performance?"]
    },
    "Cybersecurity": {
        "Beginner": ["What is phishing?", "What is malware?", "What is firewall?"],
        "Intermediate": ["What is encryption?", "Explain hashing.", "What is vulnerability assessment?"],
        "Advanced": ["Explain penetration testing.", "What is zero trust security?", "Explain IDS vs IPS."]
    }
}

# NAVBAR
col1, col2, col3, col4, col5, col6, col7 = st.columns([3,1,1,1,1.4,1.5,1])

with col1:
    st.markdown("## 💼 AI RESUME ANALYZER")
with col2:
    if st.button("Home", key="nav_home"):
        st.session_state.page = "Home"
with col3:
    if st.button("About", key="nav_about"):
        st.session_state.page = "About"
with col4:
    if st.button("Help", key="nav_help"):
        st.session_state.page = "Help"
with col5:
    if st.button("Job Matcher", key="nav_job"):
        st.session_state.page = "Job Matcher"
with col6:
    if st.button("Interview Qs", key="nav_interview"):
        st.session_state.page = "Interview"
with col7:
    if st.button("☀️/🌙", key="nav_theme"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# HOME
if st.session_state.page == "Home":
    st.markdown("""
<div class="hero">
    <div class="hero-title">AI RESUME ANALYZER</div>
    <div class="hero-sub">
        Smart Resume Analysis • ATS Score • Job Matching • AI Interview Preparation
    </div>
</div>
""", unsafe_allow_html=True)

    st.write("")
    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown("<div class='info-box'><h3>📊 Resume Analysis</h3><p>ATS score, skills, projects, education and certificates.</p></div>", unsafe_allow_html=True)
    with colB:
        st.markdown("<div class='info-box'><h3>🎯 Job Matching</h3><p>Compare resume with job description and find missing skills.</p></div>", unsafe_allow_html=True)
    with colC:
        st.markdown("<div class='info-box'><h3>🎤 Interview Prep</h3><p>Generate beginner, intermediate and advanced questions.</p></div>", unsafe_allow_html=True)

    center = st.columns([2,1,2])
    with center[1]:
        if st.button("ACCESS ANALYZER", key="access_btn"):
            st.session_state.page = "Login"
            st.rerun()

elif st.session_state.page == "About":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">About Developer</div>', unsafe_allow_html=True)
    st.write("👨‍💻 Developer Name: Tanishq Garg")
    st.write("🎓 Computer Science & Artificial Intelligence")
    st.markdown('<div class="section-title">About Website</div>', unsafe_allow_html=True)
    st.write("""
    This website can:
    - Analyze resumes
    - Generate ATS score
    - Predict job role
    - Match resume with job description
    - Generate interview questions
    - Download analysis report
    - Rank resume level
    """)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Help":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">How Website Works</div>', unsafe_allow_html=True)
    st.write("""
    1. Create account or login  
    2. Upload resume PDF  
    3. AI reads resume text  
    4. Website detects skills, education, certificates, projects and experience  
    5. ATS score and resume rank are generated  
    6. You can download report  
    7. Use Job Matcher and Interview Questions features  
    """)
    st.markdown('<div class="section-title">Support Contact</div>', unsafe_allow_html=True)
    st.write("📞 9460460765")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Login":
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    option = st.radio("Choose Option", ["Login", "Signup"])

    if option == "Signup":
        st.subheader("Create Account")
        new_user = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")

        if st.button("Signup", key="signup_btn"):
            hashed = hash_password(new_password)
            try:
                c.execute("INSERT INTO users(username,email,password) VALUES(?,?,?)", (new_user, new_email, hashed))
                conn.commit()
                st.success("Account Created Successfully")
            except:
                st.error("Email already exists")
    else:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", key="login_btn"):
            hashed = hash_password(password)
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed))
            data = c.fetchone()
            if data:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.page = "Dashboard"
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Email or Password")

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Dashboard":
    if not st.session_state.logged_in:
        st.session_state.page = "Login"
        st.rerun()

    st.markdown('<div class="section-title">👤 User Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='info-box'>Welcome: <b>{st.session_state.user_email}</b><br><br>Choose any feature from below:</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Open Resume Analyzer", key="dash_analyzer"):
            st.session_state.page = "Analyzer"
            st.rerun()
    with c2:
        if st.button("Open Job Matcher", key="dash_job"):
            st.session_state.page = "Job Matcher"
            st.rerun()
    with c3:
        if st.button("Open Interview Prep", key="dash_interview"):
            st.session_state.page = "Interview"
            st.rerun()

elif st.session_state.page == "Analyzer":
    if not st.session_state.logged_in:
        st.warning("Please Login First")
        st.session_state.page = "Login"
        st.rerun()

    st.markdown("## 📄 Upload Resume")

    if st.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.page = "Home"
        st.rerun()

    uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner("Analyzing Resume... Please wait"):
            text = read_pdf(uploaded_file)

        st.markdown('<div class="card">', unsafe_allow_html=True)

        lines = text.split("\n")
        candidate_name = lines[0] if lines else "Candidate"

        found_skills = [skill for skill in skills if skill.lower() in text.lower()]

        education_text = get_section(text, ["education", "academic background"], ["skills", "projects", "experience", "certificates", "certifications"])
        education_lines = clean_lines(education_text)

        certificate_text = get_section(text, ["certificates", "certifications", "certificate"], ["projects", "skills", "education", "experience"])
        certificate_lines = clean_lines(certificate_text)

        project_text = get_section(text, ["projects", "project"], ["certificates", "certifications", "education", "skills", "experience"])
        project_lines = clean_lines(project_text)

        experience_text = get_section(text, ["experience", "work experience", "internship"], ["education", "skills", "projects", "certificates", "certifications"])
        experience_lines = clean_lines(experience_text)

        score = 45
        if len(found_skills) >= 8:
            score += 18
        elif len(found_skills) >= 5:
            score += 12
        else:
            score += 5
        if education_lines:
            score += 7
        if project_lines:
            score += 8
        if certificate_lines:
            score += 8
        if experience_lines:
            score += 8
        if len(text.split()) > 250:
            score += 8
        if "github" in text.lower():
            score += 4
        if score > 92:
            score = 92

        rank = get_rank(score)

        st.markdown('<div class="section-title">👤 Candidate Name</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>{candidate_name}</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">🚀 Skills Found</div>', unsafe_allow_html=True)
        if found_skills:
            for skill in found_skills:
                st.markdown(f"<div class='skill-box'>{skill}</div>", unsafe_allow_html=True)
        else:
            st.warning("No Skills Found")

        st.markdown(f"<div class='score-box'>ATS Resume Score: {score}/100</div>", unsafe_allow_html=True)
        st.progress(score)

        st.markdown('<div class="section-title">🏆 Resume Rank</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'><b>{rank}</b> Level Resume</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">🎓 Education</div>', unsafe_allow_html=True)
        if education_lines:
            for line in education_lines:
                if line.lower() not in ["education", "academic background"]:
                    st.write("•", line)
        else:
            st.warning("No Education Details Found")

        st.markdown('<div class="section-title">📜 Certificates</div>', unsafe_allow_html=True)
        if certificate_lines:
            for line in certificate_lines:
                if line.lower() not in ["certificate", "certificates", "certifications"]:
                    st.write("•", line)
        else:
            st.warning("No Certificate Details Found")

        st.markdown('<div class="section-title">🛠 Projects</div>', unsafe_allow_html=True)
        if project_lines:
            for line in project_lines:
                if line.lower() not in ["project", "projects"]:
                    st.write("•", line)
        else:
            st.warning("No Project Details Found")

        st.markdown('<div class="section-title">💼 Experience</div>', unsafe_allow_html=True)
        if experience_lines:
            for line in experience_lines:
                if line.lower() not in ["experience", "work experience", "internship"]:
                    st.write("•", line)
        else:
            st.warning("No Experience Details Found")

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

        st.markdown('<div class="section-title">💼 Predicted Job Role</div>', unsafe_allow_html=True)
        st.success(role)

        improvement = ""
        if not education_lines:
            improvement += "• Add proper education details.<br>"
        if not project_lines:
            improvement += "• Add strong projects with technology used, features and GitHub link.<br>"
        if not certificate_lines:
            improvement += "• Add industry certificates like Google, AWS, IBM, Cisco, Coursera etc.<br>"
        if not experience_lines:
            improvement += "• Add internship, freelance work or practical experience.<br>"
        if "github" not in text.lower():
            improvement += "• Add GitHub profile link.<br>"
        improvement += "• Add measurable achievements with numbers.<br>"
        improvement += "• Use job-specific keywords.<br>"
        improvement += "• Improve project descriptions with problem, solution and impact.<br>"

        st.markdown('<div class="section-title">🚀 AI Resume Suggestions</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>{improvement}</div>", unsafe_allow_html=True)

        top_skills = ", ".join(found_skills[:5]) if found_skills else "technical skills"
        summary = f"""
        <b>{candidate_name}</b> has skills in <b>{top_skills}</b>.<br><br>
        ATS Score: <b>{score}/100</b><br>
        Resume Rank: <b>{rank}</b><br>
        Suitable Role: <b>{role}</b>
        """
        st.markdown('<div class="section-title">📝 Smart Resume Summary</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>{summary}</div>", unsafe_allow_html=True)

        report_text = make_report_text(candidate_name, score, role, found_skills, rank, improvement)
        st.download_button("📥 Download Resume Analysis Report", report_text, "resume_analysis_report.txt", "text/plain")

        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Job Matcher":
    st.markdown("## 🎯 Resume vs Job Description Matcher")

    resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])
    job_description = st.text_area("Paste Job Description")

    if resume_file and job_description:
        with st.spinner("Matching Resume With Job Description..."):
            resume_text = read_pdf(resume_file)

        matched = []
        missing = []

        for skill in skills:
            if skill.lower() in job_description.lower():
                if skill.lower() in resume_text.lower():
                    matched.append(skill)
                else:
                    missing.append(skill)

        total = len(matched) + len(missing)
        match_score = int((len(matched) / total) * 100) if total > 0 else 0

        st.markdown(f"<div class='score-box'>Match Score: {match_score}%</div>", unsafe_allow_html=True)
        st.progress(match_score)

        st.subheader("✅ Matching Skills")
        for item in matched:
            st.success(item)

        st.subheader("❌ Missing Skills")
        for item in missing:
            st.warning(item)

elif st.session_state.page == "Interview":
    st.markdown("## 🎤 AI Interview Questions")

    level = st.selectbox("Choose Difficulty Level", ["Beginner", "Intermediate", "Advanced"])

    file = st.file_uploader("Upload Resume PDF", type=["pdf"])

    if file:
        with st.spinner("Generating Interview Questions..."):
            text = read_pdf(file)

        found = [skill for skill in skills if skill.lower() in text.lower()]

        if found:
            for skill in found:
                if skill in question_bank:
                    st.markdown(f"<div class='section-title'>{skill} Questions</div>", unsafe_allow_html=True)
                    for q in question_bank[skill][level]:
                        st.markdown(f"<div class='info-box'>• {q}</div>", unsafe_allow_html=True)
        else:
            st.warning("No skills found for interview question generation.")