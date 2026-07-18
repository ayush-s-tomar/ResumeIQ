"""
ResumeIQ — AI-Powered Resume Screener (Streamlit Edition)
Rebuilt from the original Flask app, same scoring logic + Groq prompts.
"""

import hashlib
import json
import os
import time
from datetime import datetime

import pdfplumber
import streamlit as st
from groq import Groq

# ─────────────────────────── Page config ───────────────────────────
st.set_page_config(
    page_title="ResumeIQ — AI Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────── Config / constants ───────────────────────────
MIN_RESUME_LENGTH, MAX_RESUME_LENGTH = 100, 15_000
MIN_JD_LENGTH, MAX_JD_LENGTH = 30, 8_000
MIN_EXTRACTED_TEXT_LENGTH = 50
PDF_MAGIC_BYTES = b"%PDF-"
MAX_UPLOAD_MB = 5
CACHE_TTL_SECONDS = 60 * 60
MODEL_NAME = "llama-3.3-70b-versatile"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

JD_TEMPLATES = {
    "🐍 Python Developer": """We are looking for a skilled Python Developer to join our backend engineering team.

Key Responsibilities:
- Design and develop scalable REST APIs using Flask or FastAPI
- Write clean, maintainable Python code following best practices
- Work with databases (PostgreSQL, MongoDB) and ORM frameworks
- Integrate third-party APIs and services
- Participate in code reviews and agile ceremonies

Requirements:
- 2+ years of Python development experience
- Strong knowledge of Flask or FastAPI
- Experience with REST API design and JSON
- Familiarity with Git, Docker, and CI/CD pipelines
- Knowledge of SQL and NoSQL databases
- Problem-solving skills and attention to detail

Nice to have:
- Experience with cloud platforms (AWS, GCP, Azure)
- Knowledge of message queues (Celery, RabbitMQ)
- Contributions to open-source projects""",
    "🤖 AI / ML Engineer": """We are hiring an AI/ML Engineer to build and deploy intelligent systems at scale.

Key Responsibilities:
- Design, train, and evaluate machine learning models
- Build NLP pipelines and LLM-powered applications
- Deploy models to production using MLflow, FastAPI, or similar tools
- Work with large datasets and perform feature engineering
- Collaborate with product teams to integrate AI into applications

Requirements:
- Strong Python skills with experience in ML frameworks (PyTorch, TensorFlow, scikit-learn)
- Hands-on experience with NLP, LLMs, or computer vision
- Familiarity with Hugging Face, LangChain, or OpenAI APIs
- Understanding of model evaluation, fine-tuning, and prompt engineering
- Experience with data preprocessing and EDA
- Knowledge of Git and experiment tracking tools

Nice to have:
- Experience with vector databases (Pinecone, Weaviate)
- Knowledge of MLOps and model deployment pipelines
- Published research or Kaggle competition experience""",
    "📊 Data Analyst": """We are looking for a Data Analyst to turn raw data into actionable business insights.

Key Responsibilities:
- Analyze large datasets to identify trends, patterns, and anomalies
- Build dashboards and reports using Power BI or Tableau
- Write complex SQL queries for data extraction and transformation
- Work with stakeholders to define KPIs and metrics
- Present findings clearly to non-technical audiences

Requirements:
- Proficiency in SQL (joins, window functions, CTEs)
- Experience with Python or R for data analysis (pandas, NumPy, matplotlib)
- Hands-on experience with BI tools (Power BI, Tableau, or Looker)
- Strong understanding of statistics and data visualization
- Excellent communication and storytelling skills

Nice to have:
- Experience with Google Analytics or similar tools
- Knowledge of data warehouses (BigQuery, Snowflake, Redshift)
- Familiarity with Excel advanced features and pivot tables""",
    "🌐 Full Stack Developer": """We are seeking a Full Stack Developer to build end-to-end web applications.

Key Responsibilities:
- Develop responsive frontend interfaces using React or Vue.js
- Build robust backend APIs using Node.js or Python (Django/Flask)
- Design and manage relational and non-relational databases
- Ensure application performance, security, and scalability
- Collaborate with UI/UX designers and product managers

Requirements:
- 2+ years of full stack development experience
- Strong proficiency in JavaScript/TypeScript and React or Vue.js
- Backend experience with Node.js, Python, or similar
- Knowledge of HTML5, CSS3, and responsive design
- Experience with REST APIs and GraphQL
- Familiarity with Git, Docker, and deployment platforms (Vercel, Render, AWS)

Nice to have:
- Experience with Next.js or Nuxt.js
- Knowledge of WebSockets and real-time applications
- Understanding of CI/CD pipelines and DevOps basics""",
}

# ─────────────────────────── Styling (matches Flask UI) ───────────────────────────
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)
st.markdown("""
<style>
:root {
  --bg: #F5F2EE; --surface: #FFFFFF; --surface2: #FAFAF8;
  --border: #E8E3DC; --text: #1A1714; --text-muted: #8A8178;
  --accent: #2D6A4F; --accent-light: #D8F3DC;
  --accent2: #B7410E; --accent2-light: #FDE8DF;
  --warn: #C77B2F; --warn-light: #FEF3E2;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: var(--bg); }
#MainMenu, footer, header {visibility: hidden;}

.riq-header { display:flex; align-items:center; justify-content:space-between; padding: 4px 0 20px 0; border-bottom: 1px solid var(--border); margin-bottom: 8px;}
.riq-logo { font-family:'DM Serif Display', serif; font-size:26px; color:var(--text); }
.riq-logo .dot { display:inline-block; width:9px; height:9px; background:var(--accent); border-radius:50%; margin-right:8px;}
.riq-badge { font-size:11px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); background:var(--accent-light); padding:5px 12px; border-radius:20px; }

.riq-hero { text-align:center; padding: 28px 10px 8px; }
.riq-tag { font-size:12px; font-weight:600; letter-spacing:.1em; text-transform:uppercase; color:var(--text-muted); }
.riq-hero h1 { font-family:'DM Serif Display', serif; font-size:42px; line-height:1.15; margin:10px 0 12px; color:var(--text);}
.riq-hero h1 em { font-style:italic; color:var(--accent);}
.riq-hero p { font-size:16px; color:var(--text-muted); font-weight:300; max-width:520px; margin:0 auto;}

.riq-card { background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:24px 26px; box-shadow:0 2px 20px rgba(26,23,20,0.06); margin-bottom: 16px;}
.riq-card-title { font-family:'DM Serif Display', serif; font-size:19px; display:flex; align-items:center; gap:10px; margin-bottom:14px; color:var(--text);}
.riq-num { width:26px; height:26px; background:var(--text); color:white; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:12px; font-weight:600;}

.score-card { background:var(--text); color:white; border-radius:16px; padding:30px 34px; margin-bottom:20px; }
.score-num { font-family:'DM Serif Display', serif; font-size:46px; line-height:1; text-align:center;}
.score-label { font-size:11px; opacity:.6; text-transform:uppercase; letter-spacing:.08em; text-align:center;}
.verdict-pill { display:inline-block; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:600; margin-bottom:10px;}
.verdict-strong { background:#D8F3DC; color:#2D6A4F;}
.verdict-good { background:#EAF4FB; color:#1B6CA8;}
.verdict-partial { background:#FEF3E2; color:#C77B2F;}
.verdict-weak { background:#FDE8DF; color:#B7410E;}

.tag-matched { display:inline-block; background:var(--accent-light); color:var(--accent); padding:5px 12px; border-radius:20px; font-size:13px; font-weight:500; margin:3px;}
.tag-missing { display:inline-block; background:var(--accent2-light); color:var(--accent2); padding:5px 12px; border-radius:20px; font-size:13px; font-weight:500; margin:3px;}

.riq-list-item { font-size:14px; color:var(--text); padding:5px 0; }
.dot-green::before { content:"● "; color:var(--accent); }
.dot-warn::before { content:"● "; color:var(--warn); }

.result-title { font-size:12px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--text-muted); margin-bottom:10px;}

.riq-footer { text-align:center; padding:24px; color:var(--text-muted); font-size:13px; border-top:1px solid var(--border); margin-top:30px;}
.riq-footer a { color:var(--accent); text-decoration:none;}

div.stButton > button {
  border-radius: 100px; font-weight:600; border:1px solid var(--border); background:white; color:var(--text);
}
div.stButton > button:hover { border-color:var(--accent); color:var(--accent);}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── Groq helpers (same logic as app.py) ───────────────────────────
@st.cache_resource
def get_client():
    if not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)


def _strip_fences(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def call_groq_json(prompt, max_tokens=1500, temperature=0.0):
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    raw = _strip_fences(response.choices[0].message.content)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        retry_prompt = (
            prompt
            + "\n\nYour previous response was not valid JSON. "
              "Return ONLY the raw JSON object/array with no extra text, "
              "no markdown fences, and no commentary."
        )
        retry_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": retry_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        raw_retry = _strip_fences(retry_response.choices[0].message.content)
        return json.loads(raw_retry)


def analyze_resume(resume_text, job_description):
    prompt = f"""You are an expert ATS and career coach. Analyze the resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY a valid JSON object with this exact structure:
{{
  "match_score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "matched_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword1", "keyword2"],
  "strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2", "improvement3"],
  "verdict": "<one of: Strong Match | Good Match | Partial Match | Weak Match>"
}}"""
    return call_groq_json(prompt, max_tokens=1500)


def generate_cover_letter(resume_text, job_description):
    client = get_client()
    prompt = f"""You are an expert career coach. Write a professional, personalized cover letter based on the resume and job description below.

Rules:
- Keep it to 3-4 paragraphs
- Start with a strong opening (do NOT start with "I am writing to apply")
- Highlight 2-3 specific skills that match the job description
- End with a confident call to action
- Do NOT use placeholders like [Company Name] or [Your Name]
- Return ONLY the cover letter text, no extra commentary

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800,
    )
    return response.choices[0].message.content.strip()


def generate_interview_prep(resume_text, job_description):
    prompt = f"""You are an expert technical interviewer and career coach.
Based on the candidate's resume and the job description, generate exactly 5 likely interview questions this candidate will face.

For each question:
- Make it specific to THIS candidate and THIS role — not generic
- Include the type: Technical / Behavioural / Situational
- Give a concise tip on how to answer it well (2-3 sentences max)

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question": "<the interview question>",
    "type": "<Technical | Behavioural | Situational>",
    "tip": "<how to answer this well>"
  }}
]

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""
    return call_groq_json(prompt, max_tokens=1200, temperature=0.7)


def extract_text_from_pdf(file_bytes):
    import io
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def validate_text_length(text, min_len, max_len, field_name):
    if len(text) < min_len:
        return f"{field_name} seems too short (minimum {min_len} characters)."
    if len(text) > max_len:
        return f"{field_name} is too long (maximum {max_len:,} characters). Please trim it down."
    return None


def make_cache_key(*parts):
    raw = "||".join(parts)
    return "resumeiq:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def cache_get(key):
    store = st.session_state.setdefault("_cache", {})
    entry = store.get(key)
    if not entry:
        return None
    value, expires_at = entry
    if time.time() > expires_at:
        store.pop(key, None)
        return None
    return value


def cache_set(key, value):
    store = st.session_state.setdefault("_cache", {})
    store[key] = (value, time.time() + CACHE_TTL_SECONDS)


def verdict_class(v):
    if "Strong" in v:
        return "verdict-strong", "🟢"
    if "Good" in v:
        return "verdict-good", "🔵"
    if "Partial" in v:
        return "verdict-partial", "🟡"
    return "verdict-weak", "🔴"


def build_analysis_pdf(data, job_desc_snippet):
    from fpdf import FPDF

    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    pdf.set_fill_color(26, 23, 20)
    pdf.rect(0, 0, 210, 26, style="F")
    pdf.set_xy(20, 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 8, "ResumeIQ", ln=1)
    pdf.set_x(20)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 6, "AI-Powered Resume Analysis Report", ln=1)

    pdf.set_y(36)
    pdf.set_text_color(26, 23, 20)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 10, f"Score: {data['match_score']} / 100", ln=1)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, data["verdict"], ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, data["summary"])
    pdf.ln(4)

    def section(title, items):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(138, 129, 120)
        pdf.cell(0, 8, title.upper(), ln=1)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        for item in items:
            pdf.multi_cell(0, 6, f"- {item}")
        pdf.ln(2)

    section("Matched Keywords", data.get("matched_keywords", []))
    section("Missing Keywords", data.get("missing_keywords", []))
    section("Strengths", data.get("strengths", []))
    section("Areas to Improve", data.get("improvements", []))

    return bytes(pdf.output(dest="S"))


def build_cover_letter_pdf(letter_text):
    from fpdf import FPDF

    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    pdf.set_fill_color(26, 23, 20)
    pdf.rect(0, 0, 210, 22, style="F")
    pdf.set_xy(20, 6)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "ResumeIQ", ln=1)
    pdf.set_y(30)
    pdf.set_text_color(26, 23, 20)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "Cover Letter", ln=1)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(40, 40, 40)
    for para in letter_text.split("\n\n"):
        pdf.multi_cell(0, 6, para.strip())
        pdf.ln(3)
    return bytes(pdf.output(dest="S"))


# ─────────────────────────── Session state ───────────────────────────
for key, default in [
    ("results", None), ("resume_text_used", ""), ("job_desc", ""),
    ("cover_letter", None), ("interview_qs", None), ("history", []),
]:
    st.session_state.setdefault(key, default)

# ─────────────────────────── Header ───────────────────────────
st.markdown("""
<div class="riq-header">
  <div class="riq-logo"><span class="dot"></span>ResumeIQ</div>
  <span class="riq-badge">AI Powered</span>
</div>
<div class="riq-hero">
  <div class="riq-tag">Smart Resume Analysis</div>
  <h1>Match your resume to<br/><em>any job description</em></h1>
  <p>Paste your resume and a job posting. Get an instant AI-powered match score with actionable feedback.</p>
</div>
""", unsafe_allow_html=True)

if not GROQ_API_KEY:
    st.warning("⚠️ GROQ_API_KEY is not set. Add it in Streamlit Cloud → App settings → Secrets before deploying.")

# ─────────────────────────── JD Templates ───────────────────────────
st.markdown("<p style='text-align:center;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--text-muted);'>Quick Templates</p>", unsafe_allow_html=True)
tcols = st.columns(4)
for i, (label, text) in enumerate(JD_TEMPLATES.items()):
    if tcols[i].button(label, use_container_width=True, key=f"tpl_{i}"):
        st.session_state["job_desc"] = text

# ─────────────────────────── Input cards ───────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="riq-card"><div class="riq-card-title"><span class="riq-num">1</span> Your Resume</div>', unsafe_allow_html=True)
    tab_upload, tab_paste = st.tabs(["📄 Upload PDF", "✏️ Paste Text"])
    uploaded_file = None
    pasted_resume = ""
    with tab_upload:
        uploaded_file = st.file_uploader("Upload your resume (PDF, max 5MB)", type=["pdf"], label_visibility="collapsed")
    with tab_paste:
        pasted_resume = st.text_area("Paste your resume text here...", height=220, label_visibility="collapsed", key="resume_text_input")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="riq-card"><div class="riq-card-title"><span class="riq-num">2</span> Job Description</div>', unsafe_allow_html=True)
    job_desc = st.text_area(
        "Paste the job description here...",
        height=270, label_visibility="collapsed", key="job_desc",
    )
    st.caption(f"{len(job_desc)} characters")
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────── Analyze ───────────────────────────
_, mid, _ = st.columns([1, 1, 1])
analyze_clicked = mid.button("✦  Analyze Match", use_container_width=True, type="primary")

if analyze_clicked:
    jd = job_desc.strip()
    resume_text = ""
    error = None

    if not jd:
        error = "Please paste a job description."
    elif uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        if len(file_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
            error = f"File is too large. Maximum upload size is {MAX_UPLOAD_MB} MB."
        elif file_bytes[:5] != PDF_MAGIC_BYTES:
            error = "That file doesn't look like a valid PDF. Please upload a real PDF."
        else:
            try:
                resume_text = extract_text_from_pdf(file_bytes)
            except Exception:
                error = "Could not read the uploaded PDF. Please try another file."
            if not error and len(resume_text) < MIN_EXTRACTED_TEXT_LENGTH:
                error = ("This looks like a scanned PDF with no selectable text. "
                          "Please paste your resume text directly instead.")
    elif pasted_resume.strip():
        resume_text = pasted_resume.strip()
    else:
        error = "Please upload a PDF or paste your resume text."

    if not error:
        jd_err = validate_text_length(jd, MIN_JD_LENGTH, MAX_JD_LENGTH, "Job description")
        resume_err = validate_text_length(resume_text, MIN_RESUME_LENGTH, MAX_RESUME_LENGTH, "Resume text") if resume_text else None
        error = jd_err or resume_err

    if error:
        st.error(error)
    elif not GROQ_API_KEY:
        st.error("GROQ_API_KEY is not configured — cannot run analysis.")
    else:
        cache_key = make_cache_key("analyze", resume_text, jd)
        cached = cache_get(cache_key)
        with st.spinner("🔍 Analyzing your resume, please wait..."):
            try:
                data = cached or analyze_resume(resume_text, jd)
                if not cached:
                    cache_set(cache_key, data)
            except Exception as e:
                st.error("An error occurred while analyzing your resume. Please try again.")
                data = None

        if data:
            st.session_state["results"] = data
            st.session_state["resume_text_used"] = resume_text
            st.session_state["cover_letter"] = None
            st.session_state["interview_qs"] = None
            entry = {
                "score": data["match_score"], "verdict": data["verdict"],
                "summary": data["summary"], "jd_snippet": jd[:80],
                "matched": data["matched_keywords"], "missing": data["missing_keywords"],
                "strengths": data["strengths"], "improvements": data["improvements"],
                "time": datetime.now().strftime("%d %b, %I:%M %p"),
            }
            st.session_state["history"] = ([entry] + st.session_state["history"])[:5]

# ─────────────────────────── Results ───────────────────────────
data = st.session_state["results"]
if data:
    v_class, v_emoji = verdict_class(data["verdict"])
    st.markdown(f"""
    <div class="score-card">
      <div style="display:flex; align-items:center; gap:36px;">
        <div style="width:110px;height:110px;border-radius:50%;background:rgba(255,255,255,0.1);
                    border:3px solid rgba(255,255,255,0.2);display:flex;flex-direction:column;
                    align-items:center;justify-content:center;flex-shrink:0;">
          <div class="score-num">{data['match_score']}</div>
          <div class="score-label">Score</div>
        </div>
        <div style="flex:1;">
          <div class="verdict-pill {v_class}">{v_emoji} {data['verdict']}</div>
          <div style="font-size:15px;opacity:.85;font-weight:300;line-height:1.6;">{data['summary']}</div>
          <div style="margin-top:14px;height:6px;background:rgba(255,255,255,0.15);border-radius:3px;overflow:hidden;">
            <div style="height:100%;width:{data['match_score']}%;background:#52B788;border-radius:3px;"></div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="riq-card"><div class="result-title">🟢 Matched Keywords</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<span class="tag-matched">{k}</span>' for k in data["matched_keywords"]), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with r2:
        st.markdown('<div class="riq-card"><div class="result-title">🟠 Missing Keywords</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<span class="tag-missing">{k}</span>' for k in data["missing_keywords"]), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    r3, r4 = st.columns(2)
    with r3:
        st.markdown('<div class="riq-card"><div class="result-title">💪 Strengths</div>', unsafe_allow_html=True)
        for s in data["strengths"]:
            st.markdown(f'<div class="riq-list-item dot-green">{s}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with r4:
        st.markdown('<div class="riq-card"><div class="result-title">📈 Areas to Improve</div>', unsafe_allow_html=True)
        for s in data["improvements"]:
            st.markdown(f'<div class="riq-list-item dot-warn">{s}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Actions ──
    a1, a2, a3 = st.columns(3)

    try:
        pdf_bytes = build_analysis_pdf(data, job_desc[:80])
        a1.download_button("📄 Export Analysis PDF", data=pdf_bytes,
                            file_name="ResumeIQ_Analysis.pdf", mime="application/pdf",
                            use_container_width=True)
    except Exception:
        a1.button("📄 Export PDF (unavailable)", disabled=True, use_container_width=True)

    if a2.button("✉️ Generate Cover Letter", use_container_width=True):
        with st.spinner("Generating your cover letter..."):
            try:
                st.session_state["cover_letter"] = generate_cover_letter(
                    st.session_state["resume_text_used"], job_desc.strip()
                )
            except Exception:
                st.error("Could not generate a cover letter. Please try again.")

    if a3.button("🎯 Interview Prep", use_container_width=True):
        with st.spinner("Generating your interview questions..."):
            try:
                st.session_state["interview_qs"] = generate_interview_prep(
                    st.session_state["resume_text_used"], job_desc.strip()
                )
            except Exception:
                st.error("Could not generate interview questions. Please try again.")

    if st.session_state["cover_letter"]:
        with st.expander("✉️ Cover Letter", expanded=True):
            letter = st.text_area("Cover letter", value=st.session_state["cover_letter"], height=280, label_visibility="collapsed")
            try:
                cl_pdf = build_cover_letter_pdf(letter)
                st.download_button("📥 Download as PDF", data=cl_pdf,
                                    file_name="Cover_Letter_ResumeIQ.pdf", mime="application/pdf")
            except Exception:
                pass

    if st.session_state["interview_qs"]:
        with st.expander("🎯 Interview Prep", expanded=True):
            for i, q in enumerate(st.session_state["interview_qs"], 1):
                st.markdown(f"**{i}. {q['question']}**  \n`{q['type']}`")
                st.info(f"💡 {q['tip']}")

# ─────────────────────────── History ───────────────────────────
if st.session_state["history"]:
    st.markdown("### Recent Analyses")
    for i, entry in enumerate(st.session_state["history"]):
        v_class, v_emoji = verdict_class(entry["verdict"])
        cols = st.columns([1, 5, 2])
        cols[0].markdown(f"<div style='font-family:DM Serif Display,serif;font-size:32px;'>{entry['score']}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"**{entry['jd_snippet']}…**  \n<span style='color:var(--text-muted);font-size:12px;'>🕐 {entry['time']}</span>", unsafe_allow_html=True)
        cols[2].markdown(f"<div class='verdict-pill {v_class}'>{v_emoji} {entry['verdict']}</div>", unsafe_allow_html=True)
    if st.button("🗑 Clear History"):
        st.session_state["history"] = []
        st.rerun()

# ─────────────────────────── Footer ───────────────────────────
st.markdown("""
<div class="riq-footer">
  Built by Ayush Singh Tomar &nbsp;|&nbsp;
  <a href="https://github.com/ayush-s-tomar/ResumeIQ" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)