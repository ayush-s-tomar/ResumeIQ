from flask import Flask, render_template, request, jsonify
from groq import Groq
import pdfplumber
import os
import json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def analyze_resume(resume_text, job_description):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    job_description = request.form.get('job_description', '').strip()
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400

    resume_text = ""

    if 'resume_pdf' in request.files:
        file = request.files['resume_pdf']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            try:
                resume_text = extract_text_from_pdf(filepath)
            finally:
                os.remove(filepath)

    if not resume_text:
        resume_text = request.form.get('resume_text', '').strip()

    if not resume_text:
        return jsonify({'error': 'Please upload a PDF or paste your resume text'}), 400

    if len(resume_text) < 100:
        return jsonify({'error': 'Resume text seems too short. Please check your input.'}), 400

    try:
        result = analyze_resume(resume_text, job_description)
        return jsonify(result)
    except json.JSONDecodeError:
        return jsonify({'error': 'Failed to parse AI response. Please try again.'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)