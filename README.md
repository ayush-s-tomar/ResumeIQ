# ResumeIQ — AI-Powered Resume Screener

> Match your resume to any job description in seconds. Get an AI-powered ATS score, keyword breakdown, strengths analysis, cover letter, and interview prep — all in one tool.

[![CI](https://github.com/ayush-s-tomar/ResumeIQ/actions/workflows/ci.yml/badge.svg)](https://github.com/ayush-s-tomar/ResumeIQ/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://resumeiq-55h8.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](./Dockerfile)

---

## 🌐 Live Demo

👉 **[resumeiq-55h8.onrender.com](https://resumeiq-55h8.onrender.com)**

> ⚡ Hosted on Render's free tier — may take 15–20 seconds to wake up on first visit.

---

## 📸 Demo Preview

![ResumeIQ Results View](./assets/Resume_Screener_Demo.png)

*Upload your resume, paste a job description, and get an instant AI-powered match score with keyword breakdown, strengths, and improvement suggestions.*

---

## 📑 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Docker](#-docker)
- [Running Tests](#-running-tests)
- [How to Use](#-how-to-use)
- [Deployment](#️-deployment-free-on-render)
- [Roadmap](#-roadmap)
- [What I Learned](#-what-i-learned)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **ATS Match Score** | 0–100 compatibility score against any job description |
| 🔍 **Keyword Analysis** | See exactly which keywords match and which are missing |
| 💪 **Strengths** | Understand what makes your resume stand out for this role |
| 📈 **Improvements** | Get specific, actionable suggestions to close skill gaps |
| ✉️ **Cover Letter Generator** | AI-written, personalized cover letter in one click |
| 🎤 **Interview Prep** | 5 role-specific interview questions with answering tips |
| 📄 **PDF Export** | Download your full analysis or cover letter as a PDF |
| 📋 **Job Templates** | Quick-fill JD templates for Python Dev, AI/ML, Data Analyst, Full Stack |
| 🌙 **Dark Mode** | Light/dark toggle, persisted across sessions |
| 🕐 **Score History** | Last 5 analyses saved locally for quick comparison |
| 🔒 **Rate Limiting** | 10 requests/hour per user to prevent abuse |
| ⚡ **Response Caching** | Repeated resume+JD pairs served instantly, no extra API cost |

---

## 🛠 Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11, Flask 3.0 |
| AI | Groq API (LLaMA 3.3 70B) |
| PDF Parsing | pdfplumber |
| Frontend | HTML5, CSS3, Vanilla JS |
| PDF Export | jsPDF (client-side) |
| Rate Limiting | Flask-Limiter |
| Logging | Python `logging` + RotatingFileHandler |
| Testing | pytest (18 tests, Groq calls mocked) |
| CI/CD | GitHub Actions |
| Containerisation | Docker |
| Hosting | Render |

---

## 📁 Project Structure

```
ResumeIQ/
├── app.py                      # Flask backend — all routes, caching, logging, validation
├── requirements.txt            # Production dependencies (pinned)
├── requirements-dev.txt        # Dev/test dependencies
├── Dockerfile                  # One-command container build
├── .dockerignore
├── .env.example                # Environment variable template
├── .gitignore
├── LICENSE
├── assets/
│   └── Resume_Screener_Demo.png
├── templates/
│   └── index.html              # Main UI — dark mode, skeleton loader, modals
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js             # Theme toggle, skeleton, PDF export, history
├── tests/
│   └── test_app.py             # 18 pytest tests, zero real API calls
└── .github/
    └── workflows/
        └── ci.yml              # Runs tests + Docker build on every push
```

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/ayush-s-tomar/ResumeIQ.git
cd ResumeIQ
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Get a free API key from [console.groq.com](https://console.groq.com), then:
```bash
cp .env.example .env
```
Edit `.env`:
```
GROQ_API_KEY=your_groq_key_here
```

### 5. Run the app
```bash
python app.py
```
Open **http://localhost:5000**

---

## 🐳 Docker

Run the entire app in one command — no Python or virtualenv setup needed:

```bash
# Build
docker build -t resumeiq .

# Run
docker run -p 5000:5000 --env-file .env resumeiq
```

Open **http://localhost:5000**

---

## 🧪 Running Tests

The test suite covers all routes, input validation, PDF checking, caching logic, and helper functions. No real API key or Groq calls required — everything is mocked.

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

Expected output: **18 passed**

---

## 📖 How to Use

1. Upload your resume as a PDF **or** paste the text directly
2. Paste any job description (or pick a quick template)
3. Click **✦ Analyze Match**
4. Review your score, matched/missing keywords, strengths, and improvements
5. Generate a **Cover Letter** or **Interview Prep questions** in one click
6. Export the full analysis as a **PDF**

---

## ☁️ Deployment (Free on Render)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `gunicorn app:app`
6. Add environment variable: `GROQ_API_KEY` = your key
7. Deploy!

---

## 🗺 Roadmap

- [x] ATS match score with keyword analysis
- [x] Cover letter generator
- [x] Interview prep / mock Q&A
- [x] PDF export of analysis and cover letter
- [x] Score history (last 5 analyses)
- [x] Dark / light mode
- [x] Response caching
- [x] Docker support
- [x] CI pipeline with automated tests
- [ ] DOCX resume upload support
- [ ] Multi-resume comparison mode
- [ ] Resume rewrite suggestions (AI-powered)

---

## 🧠 What I Learned

- Building and structuring REST APIs with Flask
- Integrating LLM APIs (Groq — LLaMA 3.3) with structured JSON prompting
- PDF text extraction with pdfplumber and real file validation
- Input validation and rate limiting for public-facing APIs
- Structured logging with rotating file handlers for production debugging
- In-memory response caching with TTL to reduce API cost and latency
- Client-side PDF generation with jsPDF
- Writing pytest suites with mocked external dependencies
- Setting up GitHub Actions CI pipelines
- Containerising a Python web app with Docker
- Deploying to Render with environment variable management

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

## 👤 Author

Built by **[Ayush Singh Tomar](https://github.com/ayush-s-tomar)**

If this project helped you or you found it interesting, consider giving it a ⭐ on GitHub — it genuinely helps!
