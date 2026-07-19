# ResumeIQ â€” AI-Powered Resume Screener

Match your resume to any job description in seconds. Get an AI-powered ATS score, keyword breakdown, strengths analysis, cover letter, and interview prep â€” all in one tool.

[![CI](https://github.com/ayush-s-tomar/ResumeIQ/actions/workflows/ci.yml/badge.svg)](https://github.com/ayush-s-tomar/ResumeIQ/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://resume-iq-screener.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0-black.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)](Dockerfile)

## ðŸŒ Live Demo

ðŸ‘‰ **[ResumeIQ â€” AI Resume Screener Â· Streamlit](https://resume-iq-screener.streamlit.app/)**

âš¡ Hosted on Streamlit Community Cloud â€” may take a few seconds to wake up on first visit.

## ðŸ“¸ Demo Preview

<img width="1580" height="1100" alt="ResumeIQ Results View" src="https://github.com/user-attachments/assets/3c1c7a13-e3cc-485a-a3e1-fc4c1f945e6e" />

**Upload â†’ Match â†’ Improve â†’ Apply** with confidence. Paste any job description and get an instant ATS score, keyword breakdown, and clear next steps to close the gap â€” no guessing what the numbers mean.

<details>
<summary>â–¶ï¸ Watch the full walkthrough (upload â†’ analyze â†’ cover letter â†’ interview prep â†’ PDF export)</summary>

https://github.com/user-attachments/assets/82fed220-4e50-496a-8ab1-247a29330ea7

</details>

## ðŸ“‘ Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture Notes](#-architecture-notes)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Docker](#-docker)
- [Running Tests](#-running-tests)
- [How to Use](#-how-to-use)
- [Deployment](#ï¸-deployment-free-on-streamlit-community-cloud)
- [Health Check](#-health-check)
- [Roadmap](#-roadmap)
- [What I Learned](#-what-i-learned)
- [Contributing](#-contributing)
- [License](#-license)

## âœ¨ Features

| Feature | Description |
|---|---|
| ðŸŽ¯ ATS Match Score | 0â€“100 compatibility score against any job description |
| ðŸ” Keyword Analysis | See exactly which keywords match and which are missing |
| ðŸ’ª Strengths | Understand what makes your resume stand out for this role |
| ðŸ“ˆ Improvements | Get specific, actionable suggestions to close skill gaps |
| âœ‰ï¸ Cover Letter Generator | AI-written, personalized cover letter in one click |
| ðŸŽ¤ Interview Prep | 5 role-specific interview questions with answering tips |
| ðŸ“„ PDF Export | Download your full analysis or cover letter as a PDF |
| ðŸ“‹ Job Templates | Quick-fill JD templates for Python Dev, AI/ML, Data Analyst, Full Stack |
| ðŸŒ™ Dark Mode | Light/dark toggle, persisted across sessions |
| ðŸ• Score History | Last 5 analyses saved locally for quick comparison |
| ðŸ”’ Rate Limiting | 10 requests/hour per user, shared across workers via Redis |
| âš¡ Response Caching | Repeated resume+JD pairs served instantly, no extra API cost |
| ðŸ” LLM Retry on Malformed Output | Automatically re-prompts once with a stricter format instruction if the AI's JSON response fails to parse |
| ðŸ©º Health Check Endpoint | `/health` reports Groq configuration and cache backend status for uptime monitoring |
| ðŸ–¼ï¸ Scanned-PDF Detection | Flags PDFs with little to no extractable text (scanned images) with a specific, actionable error |
| ðŸ›¡ï¸ Byte-Signature File Validation | Verifies uploaded files are real PDFs by checking their actual file signature, not just the `.pdf` extension |

## ðŸ›  Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11, Flask 3.0 |
| AI | Groq API (LLaMA 3.3 70B) |
| PDF Parsing | pdfplumber |
| Frontend | HTML5, CSS3, Vanilla JS |
| PDF Export | jsPDF (client-side) |
| Rate Limiting / Cache | Flask-Limiter + Redis (falls back to in-memory if `REDIS_URL` isn't set) |
| Logging | Python logging + RotatingFileHandler, with per-request latency logging |
| Testing | pytest (18+ tests, Groq calls mocked) |
| CI/CD | GitHub Actions |
| Containerisation | Docker |
| Hosting | Streamlit Community Cloud |

## ðŸ— Architecture Notes

A couple of decisions worth calling out, since they came out of deliberately fixing earlier gaps rather than defaults:

- **Redis-backed cache & rate limiter, with automatic fallback.** The original version stored both in a plain Python dict / in-process memory, which silently breaks correctness the moment the app runs on more than one worker process â€” each worker gets its own cache (lower hit rate) and its own rate limit counter (the real limit becomes `10 Ã— number_of_workers`, not 10). Setting a `REDIS_URL` environment variable now makes both shared and correct across processes. If Redis isn't configured or isn't reachable, the app logs a warning and falls back to in-memory storage so local development still works with zero setup.
- **One automatic retry on malformed LLM JSON.** Asking an LLM to "return only JSON" doesn't guarantee it â€” an extra sentence or a missed brace used to fail the entire request. Now, if the first response doesn't parse, the app re-prompts once with an explicit "your previous response wasn't valid JSON" instruction before giving up. This meaningfully reduces failures without adding real latency in the common case (the retry only fires on the rare malformed response).
- **Scanned-PDF detection.** A PDF that "extracts successfully" but yields almost no text is almost always a scanned image with no real text layer. Instead of surfacing a generic error, the app checks extracted length and tells the user specifically to paste text instead.
- **Byte-signature validation over extension checks.** A file named `resume.pdf` isn't necessarily a PDF â€” renaming any file is trivial. The app reads the first bytes of the uploaded file and checks for the real PDF signature (`%PDF-`) before ever attempting to parse it.

## ðŸ“ Project Structure

```
ResumeIQ/
â”œâ”€â”€ app.py                      # Flask backend â€” routes, caching, logging, validation, LLM retry, health check
â”œâ”€â”€ requirements.txt            # Production dependencies (pinned)
â”œâ”€â”€ requirements-dev.txt        # Dev/test dependencies
â”œâ”€â”€ Dockerfile                  # One-command container build
â”œâ”€â”€ .dockerignore
â”œâ”€â”€ .env.example                # Environment variable template
â”œâ”€â”€ .gitignore
â”œâ”€â”€ LICENSE
â”œâ”€â”€ assets/
â”‚   â””â”€â”€ Resume_Screener_Demo.png
â”œâ”€â”€ templates/
â”‚   â””â”€â”€ index.html              # Main UI â€” dark mode, skeleton loader, modals
â”œâ”€â”€ static/
â”‚   â”œâ”€â”€ css/
â”‚   â”‚   â””â”€â”€ style.css
â”‚   â””â”€â”€ js/
â”‚       â””â”€â”€ main.js             # Theme toggle, skeleton, PDF export, history
â”œâ”€â”€ tests/
â”‚   â””â”€â”€ test_app.py             # pytest tests, zero real API calls
â””â”€â”€ .github/
    â””â”€â”€ workflows/
        â””â”€â”€ ci.yml              # Runs tests + Docker build on every push
```

## ðŸš€ Setup & Installation

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

# Optional â€” enables shared cache/rate-limiting across workers.
# If unset, the app falls back to in-memory storage automatically.
REDIS_URL=redis://localhost:6379/0
```

### 5. Run the app

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

> No Redis running locally? Leave `REDIS_URL` unset â€” the app detects this and falls back to in-memory caching, logging a warning so you know it happened. Check `/health` to confirm which backend is active.

## ðŸ³ Docker

Run the entire app in one command â€” no Python or virtualenv setup needed:

```bash
# Build
docker build -t resumeiq .

# Run
docker run -p 5000:5000 --env-file .env resumeiq
```

Open [http://localhost:5000](http://localhost:5000)

## ðŸ§ª Running Tests

The test suite covers all routes, input validation, PDF checking, caching logic, the LLM retry path, and helper functions. No real API key or Groq calls required â€” everything is mocked.

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

## ðŸ“– How to Use

1. Upload your resume as a PDF or paste the text directly
2. Paste any job description (or pick a quick template)
3. Click **âœ¦ Analyze Match**
4. Review your score, matched/missing keywords, strengths, and improvements
5. Generate a **Cover Letter** or **Interview Prep** questions in one click
6. Export the full analysis as a PDF

## â˜ï¸ Deployment (Free on Streamlit Community Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) â†’ New app
3. Connect your GitHub repo, branch `main`, and set the main file path to `streamlit_app.py`
4. Add `GROQ_API_KEY` under App settings â†’ Secrets
5. Deploy!

> The Flask version (`app.py`) also ships with a `Dockerfile` and can be deployed anywhere that runs containers (Render, Railway, Fly.io) if you'd rather use the REST API directly instead of the Streamlit UI.

## ðŸ©º Health Check

`GET /health` returns the app's actual runtime status, not just "process is alive":

```json
{
  "status": "ok",
  "groq_configured": true,
  "cache_backend": "redis",
  "redis_reachable": true
}
```

Useful for uptime monitors, or for confirming a deploy is fully wired up without digging through logs.

## ðŸ—º Roadmap

- [x] ATS match score with keyword analysis
- [x] Cover letter generator
- [x] Interview prep / mock Q&A
- [x] PDF export of analysis and cover letter
- [x] Score history (last 5 analyses)
- [x] Dark / light mode
- [x] Response caching
- [x] Docker support
- [x] CI pipeline with automated tests
- [x] Redis-backed cache & rate limiter (shared across workers)
- [x] Automatic retry on malformed LLM JSON output
- [x] `/health` endpoint for uptime monitoring
- [x] Scanned-PDF (no text layer) detection
- [ ] Server-side score history (currently client-side only, no auth system yet)
- [ ] DOCX resume upload support
- [ ] Multi-resume comparison mode
- [ ] Resume rewrite suggestions (AI-powered)
- [ ] Eval set: measure AI score accuracy against human-judged resume/JD pairs

## ðŸ§  What I Learned

- Building and structuring REST APIs with Flask
- Integrating LLM APIs (Groq â€” LLaMA 3.3) with structured JSON prompting, including handling non-deterministic malformed output with a retry strategy
- Diagnosing and fixing a real scalability bug: in-memory cache/rate-limiter state breaking correctness across multiple worker processes, fixed with Redis and a safe fallback
- PDF text extraction with pdfplumber, real file validation via byte-signature checking, and detecting edge cases like scanned images with no text layer
- Input validation and rate limiting for public-facing APIs
- Structured logging with rotating file handlers and per-request latency tracking for production debugging
- In-memory and Redis-backed response caching with TTL to reduce API cost and latency
- Client-side PDF generation with jsPDF
- Writing pytest suites with mocked external dependencies
- Setting up GitHub Actions CI pipelines
- Containerising a Python web app with Docker
- Deploying to Streamlit Community Cloud and containerized alternatives (Render, Docker) with environment variable / secrets management and a `/health` endpoint for verifying production config

## ðŸ¤ Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

## ðŸ“„ License

This project is licensed under the [MIT License](LICENSE).

## ðŸ‘¤ Author

Built by [Ayush Singh Tomar](https://github.com/ayush-s-tomar)

If this project helped you or you found it interesting, consider giving it a â­ on GitHub â€” it genuinely helps!

