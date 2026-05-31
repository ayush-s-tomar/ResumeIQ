# ResumeAI — AI-Powered Resume Screener

## 🌐 Live Demo
👉 https://resumeiq-55h8.onrender.com

## 📸 What it does
- Upload resume PDF or paste text
- Paste any job description
- Get instant AI match score
- See missing keywords and improvements

An intelligent resume screening tool that compares your resume against a job description using the Groq AI API (LLaMA 3.3). Get a match score, keyword analysis, strengths, and actionable improvement suggestions.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Groq](https://img.shields.io/badge/Groq-LLaMA3.3-orange)

---

## Features

- **Match Score** — Get a 0–100 ATS compatibility score
- **Keyword Analysis** — See which keywords match and which are missing
- **Strengths** — Understand what makes your resume stand out
- **Improvements** — Get specific suggestions to improve your resume
- **PDF Upload** — Upload your resume as a PDF or paste text directly
- **Clean UI** — Modern dark-themed interface

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python, Flask |
| AI | Anthropic Claude API |
| PDF Parsing | pdfplumber |
| Frontend | HTML, CSS, Vanilla JS |

---

## Project Structure

```
resume-screener/
├── app.py                  # Flask backend & API logic
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
├── templates/
│   └── index.html          # Main UI
└── static/
    ├── css/
    │   └── style.css       # Styles
    └── js/
        └── main.js         # Frontend logic
```

---

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/resume-screener.git
cd resume-screener
```

### 2. Create a virtual environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Get your free API key from [console.anthropic.com](https://console.anthropic.com)

Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` and add your key:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 5. Run the app
```bash
python app.py
```

Open your browser and go to: **http://localhost:5000**

---

## How to Use

1. Upload your resume as a PDF **or** paste the text
2. Paste the job description in the right panel
3. Click **Analyze Match**
4. Review your score, matched/missing keywords, and suggestions

---

## Deployment (Free on Render)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `gunicorn app:app`
6. Add environment variable: `ANTHROPIC_API_KEY` = your key
7. Deploy!

> Add `gunicorn` to `requirements.txt` before deploying: `gunicorn==22.0.0`

---

## Screenshots

> *(Add screenshots of your app here after running it)*

---

## What I Learned

- Building REST APIs with Flask
- Integrating LLM APIs (Anthropic Claude)
- PDF text extraction with pdfplumber
- Frontend form handling and async fetch
- Deploying Python web apps

---

## License

MIT License — feel free to use and modify.
