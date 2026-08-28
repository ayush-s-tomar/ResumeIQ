ResumeIQ — AI-Powered Resume Screener
Match your resume to any job description in seconds. Get an AI-powered ATS score, keyword breakdown, strengths analysis, cover letter, and interview prep — all in one tool.
� � � � � �
TL;DR
🐛 Fixed a real multi-worker scalability bug — in-memory caching and rate limiting silently break correctness once you run more than one process; now Redis-backed with automatic fallback (see Architecture Notes).
📊 Eval'd, not just claimed — ATS scoring measured against 15 hand-labeled resume/JD pairs, mean absolute error 5.0 points against human judgment, with the full method in eval/run_eval.py.
🔁 Handles LLM non-determinism — a malformed JSON response triggers one automatic re-prompt with a stricter format instruction before failing.
🛡️ Validates files by content, not extension — checks the actual PDF byte signature, since renaming any file to .pdf is trivial.
🌐 Live Demo
👉 ResumeIQ — AI Resume Screener · Streamlit
⚡ Hosted on Streamlit Community Cloud — may take a few seconds to wake up on first visit.
📸 Demo Preview
�
￼
Upload → Match → Improve → Apply with confidence. Paste any job description and get an instant ATS score, keyword breakdown, and clear next steps to close the gap — no guessing what the numbers mean.
�
�
▶️ Watch the full walkthrough (upload → analyze → cover letter → interview prep → PDF export)
https://github.com/user-attachments/assets/67348997-c992-4d03-a2ed-e9c6f25cdbeb
�

📑 Table of Contents
Features
Tech Stack
Architecture Notes
Evaluation
Project Structure
Setup & Installation
Docker
Running Tests
How to Use
Deployment
Health Check
Roadmap
What I Learned
Contributing
License
✨ Features
Feature
Description
🎯 ATS Match Score
0–100 compatibility score against any job description
🔍 Keyword Analysis
See exactly which keywords match and which are missing
💪 Strengths
Understand what makes your resume stand out for this role
📈 Improvements
Get specific, actionable suggestions to close skill gaps
✉️ Cover Letter Generator
AI-written, personalized cover letter in one click
🎤 Interview Prep
5 role-specific interview questions with answering tips
📄 PDF Export
Download your full analysis or cover letter as a PDF
📋 Job Templates
Quick-fill JD templates for Python Dev, AI/ML, Data Analyst, Full Stack
🌙 Dark Mode
Light/dark toggle, persisted across sessions
🕐 Score History
Last 5 analyses saved locally for quick comparison
🔒 Rate Limiting
10 requests/hour per user, shared across workers via Redis
⚡ Response Caching
Repeated resume+JD pairs served instantly, no extra API cost
🔁 LLM Retry on Malformed Output
Automatically re-prompts once with a stricter format instruction if the AI's JSON response fails to parse
🩺 Health Check Endpoint
/health reports Groq configuration and cache backend status for uptime monitoring
🖼️ Scanned-PDF Detection
Flags PDFs with little to no extractable text (scanned images) with a specific, actionable error
🛡️ Byte-Signature File Validation
Verifies uploaded files are real PDFs by checking their actual file signature, not just the .pdf extension
🛠 Tech Stack
Layer
Tech
Backend
Python 3.11, Flask 3.0
AI
Groq API (LLaMA 3.3 70B)
PDF Parsing
pdfplumber
Frontend
HTML5, CSS3, Vanilla JS
PDF Export
jsPDF (client-side)
Rate Limiting / Cache
Flask-Limiter + Redis (falls back to in-memory if REDIS_URL isn't set)
Logging
Python logging + RotatingFileHandler, with per-request latency logging
Testing
pytest (18+ tests, Groq calls mocked)
CI/CD
GitHub Actions
Containerisation
Docker
Hosting
Streamlit Community Cloud
🏗 Architecture Notes
A couple of decisions worth calling out, since they came out of deliberately fixing earlier gaps rather than defaults:
Redis-backed cache & rate limiter, with automatic fallback. The original version stored both in a plain Python dict / in-process memory, which silently breaks correctness the moment the app runs on more than one worker process — each worker gets its own cache (lower hit rate) and its own rate limit counter (the real limit becomes 10 × number_of_workers, not 10). Setting a REDIS_URL environment variable now makes both shared and correct across processes. If Redis isn't configured or isn't reachable, the app logs a warning and falls back to in-memory storage so local development still works with zero setup.
One automatic retry on malformed LLM JSON. Asking an LLM to "return only JSON" doesn't guarantee it — an extra sentence or a missed brace used to fail the entire request. Now, if the first response doesn't parse, the app re-prompts once with an explicit "your previous response wasn't valid JSON" instruction before giving up. This meaningfully reduces failures without adding real latency in the common case (the retry only fires on the rare malformed response).
Scanned-PDF detection. A PDF that "extracts successfully" but yields almost no text is almost always a scanned image with no real text layer. Instead of surfacing a generic error, the app checks extracted length and tells the user specifically to paste text instead.
Byte-signature validation over extension checks. A file named resume.pdf isn't necessarily a PDF — renaming any file is trivial. The app reads the first bytes of the uploaded file and checks for the real PDF signature (%PDF-) before ever attempting to parse it.
📊 Evaluation
ATS match scoring accuracy was measured against a hand-labeled set of resume/job-description pairs:
Metric
Value
Eval set size
15 hand-labeled resume/JD pairs
Mean absolute error
5.0 points
Scoring method
AI score (0–100) vs. human-judged score (0–100)
See eval/run_eval.py and eval/eval_set.json for methodology.
📁 Project Structure
ResumeIQ/
├── app.py                      # Flask backend — routes, caching, logging, validation, LLM retry, health check
├── requirements.txt            # Production dependencies (pinned)
├── requirements-dev.txt        # Dev/test dependencies
├── Dockerfile                  # One-command container build
├── .dockerignore
├── .env.example                # Environment variable template
├── .gitignore
├── LICENSE
├── assets/
│   ├── Resume_Screener_Demo.png
│   └── Resume_Screener_Demo.gif
├── eval/
│   ├── eval_set.json           # Hand-labeled resume/JD pairs with human scores
│   └── run_eval.py             # Measures AI score accuracy vs. human judgment
├── templates/
│   └── index.html              # Main UI — dark mode, skeleton loader, modals
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js             # Theme toggle, skeleton, PDF export, history
├── tests/
│   └── test_app.py             # pytest tests, zero real API calls
└── .github/
    └── workflows/
        └── ci.yml              # Runs tests + Docker build on every push
⚠️ Note: the Deployment section below references streamlit_app.py, which isn't listed in this file tree. This is worth reconciling — either that file exists and the tree above is missing it, or the deployment instructions need updating to match how the live demo is actually hosted.
🚀 Setup & Installation
1. Clone the repository
git clone https://github.com/ayush-s-tomar/ResumeIQ.git
cd ResumeIQ
2. Create a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Set up your API key
Get a free API key from console.groq.com, then:
cp .env.example .env
Edit .env:
GROQ_API_KEY=your_groq_key_here

# Optional — enables shared cache/rate-limiting across workers.
# If unset, the app falls back to in-memory storage automatically.
REDIS_URL=redis://localhost:6379/0
5. Run the app
python app.py
Open http://localhost:5000
No Redis running locally? Leave REDIS_URL unset — the app detects this and falls back to in-memory caching, logging a warning so you know it happened. Check /health to confirm which backend is active.
🐳 Docker
Run the entire app in one command — no Python or virtualenv setup needed:
# Build
docker build -t resumeiq .

# Run
docker run -p 5000:5000 --env-file .env resumeiq
Open http://localhost:5000
🧪 Running Tests
The test suite covers all routes, input validation, PDF checking, caching logic, the LLM retry path, and helper functions. No real API key or Groq calls required — everything is mocked.
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
📖 How to Use
Upload your resume as a PDF or paste the text directly
Paste any job description (or pick a quick template)
Click ✦ Analyze Match
Review your score, matched/missing keywords, strengths, and improvements
Generate a Cover Letter or Interview Prep questions in one click
Export the full analysis as a PDF
☁️ Deployment (Free on Streamlit Community Cloud)
Push this repo to GitHub
Go to share.streamlit.io → New app
Connect your GitHub repo, branch main, and set the main file path to streamlit_app.py
Add GROQ_API_KEY under App settings → Secrets
Deploy!
The Flask version (app.py) also ships with a Dockerfile and can be deployed anywhere that runs containers (Render, Railway, Fly.io) if you'd rather use the REST API directly instead of the Streamlit UI.
🩺 Health Check
GET /health returns the app's actual runtime status, not just "process is alive":
{
  "status": "ok",
  "groq_configured": true,
  "cache_backend": "redis",
  "redis_reachable": true
}
Useful for uptime monitors, or for confirming a deploy is fully wired up without digging through logs.
🗺 Roadmap
ATS match score with keyword analysis
Cover letter generator
Interview prep / mock Q&A
PDF export of analysis and cover letter
Score history (last 5 analyses)
Dark / light mode
Response caching
Docker support
CI pipeline with automated tests
Redis-backed cache & rate limiter (shared across workers)
Automatic retry on malformed LLM JSON output
/health endpoint for uptime monitoring
Scanned-PDF (no text layer) detection
Eval harness measuring ATS score accuracy against human-judged pairs — 15-pair hand-labeled set, 5.0 mean absolute error (see Evaluation)
Server-side score history (currently client-side only, no auth system yet)
DOCX resume upload support
Multi-resume comparison mode
Resume rewrite suggestions (AI-powered)
🧠 What I Learned
Building and structuring REST APIs with Flask
Integrating LLM APIs (Groq — LLaMA 3.3) with structured JSON prompting, including handling non-deterministic malformed output with a retry strategy
Diagnosing and fixing a real scalability bug: in-memory cache/rate-limiter state breaking correctness across multiple worker processes, fixed with Redis and a safe fallback
PDF text extraction with pdfplumber, real file validation via byte-signature checking, and detecting edge cases like scanned images with no text layer
Input validation and rate limiting for public-facing APIs
Structured logging with rotating file handlers and per-request latency tracking for production debugging
In-memory and Redis-backed response caching with TTL to reduce API cost and latency
Client-side PDF generation with jsPDF
Writing pytest suites with mocked external dependencies
Setting up GitHub Actions CI pipelines
Containerising a Python web app with Docker
Deploying to Streamlit Community Cloud and containerized alternatives (Render, Docker) with environment variable / secrets management and a /health endpoint for verifying production config
🤝 Contributing
Contributions, issues, and feature requests are welcome!
Fork the repo
Create a feature branch: git checkout -b feature/your-feature
Commit your changes: git commit -m 'Add some feature'
Push to the branch: git push origin feature/your-feature
Open a Pull Request
📄 License
This project is licensed under the MIT License.
👤 Author
Built by Ayush Singh Tomar
If this project helped you or you found it interesting, consider giving it a ⭐ on GitHub — it genuinely helps!