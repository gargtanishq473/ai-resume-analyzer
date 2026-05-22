import streamlit as st
import pdfplumber
import sqlite3
import hashlib

st.set_page_config(page_title="AI Resume Analyzer", page_icon="💼", layout="wide")

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

if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

def hash_password(password):
    return hashlib.sha256((password + "resume_secret").encode()).hexdigest()

dark_css = """
<style>
.stApp{
    background:linear-gradient(-45deg,#020617,#0f172a,#1e1b4b,#312e81);
    background-size:400% 400%;
    animation:gradientBG 12s ease infinite;
    color:white;
}
@keyframes gradientBG{
    0%{background-position:0% 50%;}
    50%{background-position:100% 50%;}
    100%{background-position:0% 50%;}
}
.hero{
    padding:70px;
    border-radius:30px;
    text-align:center;
    background:rgba(255,255,255,0.06);
    backdrop-filter:blur(15px);
    animation:floatAnim 4s ease-in-out infinite;
}
@keyframes floatAnim{
    0%{transform:translateY(0);}
    50%{transform:translateY(-10px);}
    100%{transform:translateY(0);}
}
.hero-title{
    font-size:72px;
    font-weight:900;
    color:#38bdf8;
    text-shadow:0 0 20px rgba(56,189,248,0.8);
}
.hero-sub{
    font-size:22px;
    color:#dbeafe;
}
.card,.info-box,.login-card{
    background:rgba(255,255,255,0.07);
    border:1px solid rgba(255,255,255,0.18);
    border-radius:24px;
    padding:22px;
    margin-top:20px;
    backdrop-filter:blur(12px);
    box-shadow:0 0 25px rgba(34,211,238,0.15);
}
.section-title{
    font-size:34px;
    font-weight:900;
    color:#38bdf8;
    margin-top:30px;
    margin-bottom:15px;
}
.skill-box{
    background:linear-gradient(90deg,#06b6d4,#8b5cf6);
    padding:12px;
    border-radius:14px;
    margin:10px 0;
    color:white;
    font-weight:700;
}
.score-box{
    background:linear-gradient(90deg,#2563eb,#06b6d4);
    padding:28px;
    border-radius:20px;
    text-align:center;
    font-size:38px;
    font-weight:900;
    color:white;
}
.stButton>button{
    background:linear-gradient(90deg,#06b6d4,#8b5cf6);
    color:white;
    border:none;
    border-radius:14px;
    padding:12px 24px;
    font-weight:700;
}
.watermark{
    position:fixed;
    bottom:15px;
    right:25px;
    color:rgba(255,255,255,0.18);
    font-size:18px;
    font-weight:700;
}
</style>
"""

light_css = """
<style>
.stApp{
    background:linear-gradient(135deg,#f8fafc,#dbeafe,#e0f2fe);
    color:#111827;
}
.hero,.card,.info-box,.login-card{
    background:white;
    border-radius:24px;
    padding:22px;
    margin-top:20px;
    box-shadow:0 0 18px rgba(0,0,0,0.08);
}
.hero{
    padding:70px;
    text-align:center;
}
.hero-title{
    font-size:72px;
    font-weight:900;
    color:#2563eb;
}
.hero-sub{
    font-size:22px;
    color:#374151;
}
.section-title{
    font-size:34px;
    font-weight:900;
    color:#2563eb;
    margin-top:30px;
    margin-bottom:15px;
}
.skill-box,.stButton>button{
    background:linear-gradient(90deg,#2563eb,#7c3aed);
    padding:12px;
    border-radius:14px;
    color:white;
    font-weight:700;
}
.score-box{
    background:linear-gradient(90deg,#2563eb,#06b6d4);
    padding:28px;
    border-radius:20px;
    text-align:center;
    font-size:38px;
    font-weight:900;
    color:white;
}
.watermark{
    position:fixed;
    bottom:15px;
    right:25px;
    color:rgba(0,0,0,0.15);
    font-size:18px;
    font-weight:700;
}
</style>
"""

st.markdown(dark_css if st.session_state.theme == "dark" else light_css, unsafe_allow_html=True)
st.markdown('<div class="watermark">Created by Tanishq Garg</div>', unsafe_allow_html=True)

skills = ["Python","Java","C++","SQL","JavaScript","React","Cybersecurity","Machine Learning","AI","HTML","CSS"]

def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

def section_lines(text, keywords):
    lines = []
    for line in text.split("\n"):
        for key in keywords:
            if key.lower() in line.lower():
                lines.append(line.strip())
    return list(dict.fromkeys(lines))[:8]

c1,c2,c3,c4,c5,c6,c7 = st.columns([3,1,1,1,1.4,1.5,1])

with c1:
    st.markdown("## 💼 AI RESUME ANALYZER")
with c2:
    if st.button("Home", key="homebtn"):
        st.session_state.page = "home"
with c3:
    if st.button("About", key="aboutbtn"):
        st.session_state.page = "about"
with c4:
    if st.button("Help", key="helpbtn"):
        st.session_state.page = "help"
with c5:
    if st.button("Job Matcher", key="jobbtn"):
        st.session_state.page = "job"
with c6:
    if st.button("Interview Qs", key="interbtn"):
        st.session_state.page = "interview"
with c7:
    if st.button("☀️/🌙", key="themebtn"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

if st.session_state.page == "home":

    st.markdown("""
<div class="hero">
    <div class="hero-title">AI RESUME ANALYZER</div>
    <div class="hero-sub">
        Analyze resume, ATS score, job match and interview preparation
    </div>
</div>
""", unsafe_allow_html=True)

    colA,colB,colC = st.columns(3)

    with colA:
        st.markdown("<div class='info-box'><h3>📊 Resume Analysis</h3>ATS score, projects, skills, education and certificates.</div>", unsafe_allow_html=True)
    with colB:
        st.markdown("<div class='info-box'><h3>🎯 Job Matching</h3>Compare resume with job description.</div>", unsafe_allow_html=True)
    with colC:
        st.markdown("<div class='info-box'><h3>🎤 Interview Questions</h3>Generate AI interview questions.</div>", unsafe_allow_html=True)

    center = st.columns([2,1,2])
    with center[1]:
        if st.button("ACCESS ANALYZER", key="accessbtn"):
            st.session_state.page = "login"
            st.rerun()

elif st.session_state.page == "about":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">About Developer</div>', unsafe_allow_html=True)
    st.write("👨‍💻 Name: Tanishq Garg")
    st.write("🎓 Computer Science Student")
    st.write("🚀 AI & Cybersecurity Enthusiast")
    st.markdown('<div class="section-title">About Website</div>', unsafe_allow_html=True)
    st.write("""
    This website can:
    - Analyze resume
    - Generate ATS score
    - Match jobs
    - Generate interview questions
    - Detect projects and certificates
    """)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "help":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">How Website Works</div>', unsafe_allow_html=True)
    st.write("""
    1. Login or Signup  
    2. Upload Resume PDF  
    3. AI analyzes your resume  
    4. ATS score generated  
    5. Skills, projects and certificates detected  
    6. Job role prediction  
    7. Interview questions generated  
    """)
    st.markdown('<div class="section-title">Contact Support</div>', unsafe_allow_html=True)
    st.write("📞 9460460765")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "login":

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    option = st.radio("Choose Option", ["Login","Signup"])

    if option == "Signup":
        st.subheader("Create Account")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Signup", key="signupbtn"):
            hashed = hash_password(password)
            try:
                c.execute("INSERT INTO users(username,email,password) VALUES(?,?,?)", (username,email,hashed))
                conn.commit()
                st.success("Account Created Successfully")
            except:
                st.error("Email already exists")

    else:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", key="loginmainbtn"):
            hashed = hash_password(password)
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (email,hashed))
            data = c.fetchone()

            if data:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid Email or Password")

    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "dashboard":

    if not st.session_state.logged_in:
        st.session_state.page = "login"
        st.rerun()

    st.markdown('<div class="section-title">👤 User Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='info-box'>Welcome: <b>{st.session_state.user_email}</b><br><br>Choose any feature:</div>", unsafe_allow_html=True)

    col1,col2,col3 = st.columns(3)
    with col1:
        if st.button("Resume Analyzer", key="resumeopen"):
            st.session_state.page = "analyzer"
            st.rerun()
    with col2:
        if st.button("Job Matcher Open", key="jobopen"):
            st.session_state.page = "job"
            st.rerun()
    with col3:
        if st.button("Interview Questions", key="interopen"):
            st.session_state.page = "interview"
            st.rerun()

elif st.session_state.page == "analyzer":

    st.markdown("## 📄 Upload Resume")
    uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

    if uploaded_file is not None:

        text = read_pdf(uploaded_file)
        text_lower = text.lower()

        st.markdown('<div class="card">', unsafe_allow_html=True)

        candidate_name = text.split("\n")[0] if text.split("\n") else "Candidate"

        found_skills = [skill for skill in skills if skill.lower() in text_lower]

        education_lines = section_lines(text, ["b.tech","bachelor","master","mca","bca","computer science","engineering","university","college"])
        project_lines = section_lines(text, ["project","developed","built","created"])
        certificate_lines = section_lines(text, ["certificate","certification","google","aws","coursera","ibm","cisco"])
        experience_lines = section_lines(text, ["intern","experience","developer","engineer","worked"])

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
        if score > 92:
            score = 92

        if "cybersecurity" in text_lower:
            role = "Cybersecurity Analyst"
        elif "react" in text_lower:
            role = "Frontend Developer"
        elif "python" in text_lower:
            role = "Python Developer"
        elif "machine learning" in text_lower:
            role = "Machine Learning Engineer"
        else:
            role = "Software Engineer"

        st.markdown('<div class="section-title">👤 Candidate Name</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>{candidate_name}</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">🚀 Skills Found</div>', unsafe_allow_html=True)
        if found_skills:
            for skill in found_skills:
                st.markdown(f"<div class='skill-box'>{skill}</div>", unsafe_allow_html=True)
        else:
            st.warning("No skills found")

        st.markdown(f"<div class='score-box'>ATS Resume Score: {score}/100</div>", unsafe_allow_html=True)
        st.progress(score)

        st.markdown('<div class="section-title">🎓 Education</div>', unsafe_allow_html=True)
        if education_lines:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            for line in education_lines:
                st.write("•", line)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No Education Found")

        st.markdown('<div class="section-title">📜 Certificates</div>', unsafe_allow_html=True)
        if certificate_lines:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            for line in certificate_lines:
                st.write("•", line)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No Certificates Found")

        st.markdown('<div class="section-title">🚀 Projects</div>', unsafe_allow_html=True)
        if project_lines:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            for line in project_lines:
                st.write("•", line)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No Projects Found")

        st.markdown('<div class="section-title">💼 Experience</div>', unsafe_allow_html=True)
        if experience_lines:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            for line in experience_lines:
                st.write("•", line)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No Experience Found")

        st.markdown('<div class="section-title">💼 Predicted Role</div>', unsafe_allow_html=True)
        st.success(role)

        improvement = """
        • Add measurable achievements<br>
        • Add GitHub profile link<br>
        • Add portfolio website<br>
        • Add strong project descriptions<br>
        • Add internship experience<br>
        • Add industry certificates<br>
        • Use ATS friendly keywords<br>
        """

        st.markdown('<div class="section-title">🚀 How To Improve Resume</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>{improvement}</div>", unsafe_allow_html=True)

        top_skills = ", ".join(found_skills[:5]) if found_skills else "technical skills"

        summary = f"""
        <b>{candidate_name}</b> has skills in <b>{top_skills}</b>.<br><br>
        ATS Score: <b>{score}/100</b><br>
        Suitable Role: <b>{role}</b>
        """

        st.markdown('<div class="section-title">📝 Smart Resume Summary</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'>{summary}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "job":

    st.markdown("## 🎯 Resume vs Job Description")
    resume_file = st.file_uploader("Upload Resume", type=["pdf"])
    job_description = st.text_area("Paste Job Description")

    if resume_file and job_description:
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
        match_score = int((len(matched)/total)*100) if total > 0 else 0

        st.markdown(f"<div class='score-box'>Match Score: {match_score}%</div>", unsafe_allow_html=True)
        st.progress(match_score)

        st.subheader("✅ Matching Skills")
        for item in matched:
            st.success(item)

        st.subheader("❌ Missing Skills")
        for item in missing:
            st.warning(item)

elif st.session_state.page == "interview":

    st.markdown("## 🎤 AI Interview Questions")
    file = st.file_uploader("Upload Resume PDF", type=["pdf"])

    if file:
        text = read_pdf(file)

        questions = [
            "Tell me about yourself.",
            "Explain your best project.",
            "What are your strongest technical skills?",
            "Why should we hire you?",
            "Explain OOP concepts.",
            "What is Python?"
        ]

        for q in questions:
            st.markdown(f"<div class='info-box'>• {q}</div>", unsafe_allow_html=True)