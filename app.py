import hashlib
import json
import logging
import os
import time
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from groq import Groq
import pdfplumber
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

# ── Logging ──
os.makedirs('logs', exist_ok=True)

logger = logging.getLogger("resumeiq")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler('logs/app.log', maxBytes=1_000_000, backupCount=3)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(console_handler)

# ── Rate Limiter ──
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

os.makedirs('/tmp/uploads', exist_ok=True)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB hard cap, enforced by Flask itself

ALLOWED_EXTENSIONS = {'pdf'}
PDF_MAGIC_BYTES = b'%PDF-'  # real PDFs start with this signature

# ── Input validation limits ──
MIN_RESUME_LENGTH = 100
MAX_RESUME_LENGTH = 15_000       # ~3-4 pages of text, generous for any real resume
MIN_JD_LENGTH = 30
MAX_JD_LENGTH = 8_000            # generous for even a verbose JD posting

# ── Groq client ──
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Simple in-memory response cache ──
# Keyed by a hash of (endpoint + resume_text + job_description)
# Avoids paying for / waiting on a fresh Groq call when the same
# resume + JD pair is analyzed again (e.g. user double-clicks, or
# revisits the same JD with the same resume).
CACHE = {}
CACHE_TTL_SECONDS = 60 * 60  # 1 hour


def cache_get(key):
    entry = CACHE.get(key)
    if not entry:
        return None
    value, expires_at = entry
    if time.time() > expires_at:
        CACHE.pop(key, None)
        return None
    logger.info(f"Cache hit for key {key[:10]}...")
    return value


def cache_set(key, value):
    CACHE[key] = (value, time.time() + CACHE_TTL_SECONDS)


def make_cache_key(*parts):
    raw = "||".join(parts)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_valid_pdf(filepath):
    """Check the file's actual byte signature, not just its extension.
    Prevents someone renaming a .exe or .html file to .pdf."""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(5)
        return header == PDF_MAGIC_BYTES
    except Exception:
        return False


def validate_text_length(text, min_len, max_len, field_name):
    """Returns an error message string if invalid, otherwise None."""
    if len(text) < min_len:
        return f'{field_name} seems too short (minimum {min_len} characters).'
    if len(text) > max_len:
        return f'{field_name} is too long (maximum {max_len:,} characters). Please trim it down.'
    return None


def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Custom error handlers ──

@app.errorhandler(429)
def rate_limit_error(e):
    logger.warning(f"Rate limit hit by {get_remote_address()}")
    return jsonify({
        'error': '⏱ Too many requests. You can run up to 10 analyses per hour. Please try again later.'
    }), 429


@app.errorhandler(413)
def file_too_large(e):
    logger.warning(f"Upload rejected: file too large from {get_remote_address()}")
    return jsonify({'error': 'File is too large. Maximum upload size is 5 MB.'}), 413


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Unhandled 500 error: {e}", exc_info=True)
    return jsonify({'error': 'Something went wrong on our end. Please try again shortly.'}), 500


# ── Routes ──

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
@limiter.limit("10 per hour")
def analyze():
    job_description = request.form.get('job_description', '').strip()
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400

    jd_error = validate_text_length(job_description, MIN_JD_LENGTH, MAX_JD_LENGTH, 'Job description')
    if jd_error:
        return jsonify({'error': jd_error}), 400

    resume_text = ""

    if 'resume_pdf' in request.files:
        file = request.files['resume_pdf']
        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({'error': 'Only PDF files are supported.'}), 400

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if not is_valid_pdf(filepath):
                os.remove(filepath)
                logger.warning(f"Rejected non-PDF upload disguised as PDF: {filename}")
                return jsonify({'error': 'That file doesn\'t look like a valid PDF. Please upload a real PDF.'}), 400

            try:
                resume_text = extract_text_from_pdf(filepath)
            except Exception as e:
                logger.error(f"PDF extraction failed for {filename}: {e}", exc_info=True)
                return jsonify({'error': 'Could not read the uploaded PDF. Please try another file.'}), 400
            finally:
                os.remove(filepath)

    if not resume_text:
        resume_text = request.form.get('resume_text', '').strip()

    if not resume_text:
        return jsonify({'error': 'Please upload a PDF or paste your resume text'}), 400

    resume_error = validate_text_length(resume_text, MIN_RESUME_LENGTH, MAX_RESUME_LENGTH, 'Resume text')
    if resume_error:
        return jsonify({'error': resume_error}), 400

    cache_key = make_cache_key('analyze', resume_text, job_description)
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    try:
        result = analyze_resume(resume_text, job_description)
        result['resume_text'] = resume_text
        cache_set(cache_key, result)
        logger.info("Resume analysis completed successfully")
        return jsonify(result)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failure in /analyze: {e}", exc_info=True)
        return jsonify({'error': 'Failed to parse AI response. Please try again.'}), 500
    except Exception as e:
        logger.error(f"Error in /analyze: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while analyzing your resume. Please try again.'}), 500


@app.route('/cover-letter', methods=['POST'])
@limiter.limit("10 per hour")
def cover_letter():
    resume_text = request.form.get('resume_text', '').strip()
    job_description = request.form.get('job_description', '').strip()

    if not resume_text or not job_description:
        return jsonify({'error': 'Resume and job description are required.'}), 400

    resume_error = validate_text_length(resume_text, MIN_RESUME_LENGTH, MAX_RESUME_LENGTH, 'Resume text')
    if resume_error:
        return jsonify({'error': resume_error}), 400

    jd_error = validate_text_length(job_description, MIN_JD_LENGTH, MAX_JD_LENGTH, 'Job description')
    if jd_error:
        return jsonify({'error': jd_error}), 400

    cache_key = make_cache_key('cover-letter', resume_text, job_description)
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

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

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        letter = response.choices[0].message.content.strip()
        result = {'cover_letter': letter}
        cache_set(cache_key, result)
        logger.info("Cover letter generated successfully")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in /cover-letter: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while generating your cover letter. Please try again.'}), 500


@app.route('/interview-prep', methods=['POST'])
@limiter.limit("10 per hour")
def interview_prep():
    resume_text = request.form.get('resume_text', '').strip()
    job_description = request.form.get('job_description', '').strip()

    if not resume_text or not job_description:
        return jsonify({'error': 'Resume and job description are required.'}), 400

    resume_error = validate_text_length(resume_text, MIN_RESUME_LENGTH, MAX_RESUME_LENGTH, 'Resume text')
    if resume_error:
        return jsonify({'error': resume_error}), 400

    jd_error = validate_text_length(job_description, MIN_JD_LENGTH, MAX_JD_LENGTH, 'Job description')
    if jd_error:
        return jsonify({'error': jd_error}), 400

    cache_key = make_cache_key('interview-prep', resume_text, job_description)
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

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

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        questions = json.loads(raw.strip())
        result = {'questions': questions}
        cache_set(cache_key, result)
        logger.info("Interview prep questions generated successfully")
        return jsonify(result)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failure in /interview-prep: {e}", exc_info=True)
        return jsonify({'error': 'Failed to parse AI response. Please try again.'}), 500
    except Exception as e:
        logger.error(f"Error in /interview-prep: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while generating interview questions. Please try again.'}), 500


if __name__ == '__main__':
    app.run(debug=True)