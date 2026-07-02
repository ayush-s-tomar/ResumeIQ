// ── JD Templates ──
  const JD_TEMPLATES = {
    python: { text: `We are looking for a skilled Python Developer to join our backend engineering team.

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
- Contributions to open-source projects` },
    aiml: { text: `We are hiring an AI/ML Engineer to build and deploy intelligent systems at scale.

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
- Published research or Kaggle competition experience` },
    data: { text: `We are looking for a Data Analyst to turn raw data into actionable business insights.

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
- Familiarity with Excel advanced features and pivot tables` },
    fullstack: { text: `We are seeking a Full Stack Developer to build end-to-end web applications.

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
- Understanding of CI/CD pipelines and DevOps basics` }
  };

  function fillTemplate(key, btn) {
    const tpl = JD_TEMPLATES[key];
    if (!tpl) return;
    document.getElementById('jobDesc').value = tpl.text;
    document.getElementById('charCount').textContent = tpl.text.length + ' characters';
    document.querySelectorAll('.tpl-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('jobDesc').scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  // ── Theme Toggle (dark / light mode) ──
  const THEME_KEY = 'resumeiq_theme';

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
      const btn = document.getElementById('themeToggle');
      if (btn) btn.textContent = '☀️';
    } else {
      document.documentElement.removeAttribute('data-theme');
      const btn = document.getElementById('themeToggle');
      if (btn) btn.textContent = '🌙';
    }
  }

  function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const next = isDark ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  }

  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) {
      applyTheme(saved);
      return;
    }
    // No saved preference yet — respect the OS-level setting
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(prefersDark ? 'dark' : 'light');
  }

  // ── Keyword Highlighting ──
  function highlightKeywords(text, matched, missing) {
    if (!text.trim()) return;
    function escapeRegex(str) { return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
    const allKeywords = [
      ...matched.map(k => ({ word: k, type: 'matched' })),
      ...missing.map(k => ({ word: k, type: 'missing' }))
    ].sort((a, b) => b.word.length - a.word.length);
    const pattern = allKeywords.map(k => escapeRegex(k.word)).join('|');
    if (!pattern) return;
    const regex = new RegExp(`(${pattern})`, 'gi');
    const highlighted = text.replace(regex, (match) => {
      const isMatched = matched.some(k => k.toLowerCase() === match.toLowerCase());
      return `<span class="${isMatched ? 'hl-matched' : 'hl-missing'}">${match}</span>`;
    });
    document.getElementById('highlightedText').innerHTML = highlighted;
    document.getElementById('resumeText').style.display = 'none';
    document.getElementById('highlightBox').style.display = 'block';
    document.getElementById('hlLegend').style.display = 'flex';
  }

  function clearHighlights() {
    document.getElementById('highlightBox').style.display = 'none';
    document.getElementById('hlLegend').style.display = 'none';
    document.getElementById('resumeText').style.display = 'block';
  }

  // ── Modal Helpers ──
  function openModal(id) {
    document.getElementById(id).style.display = 'block';
    document.body.style.overflow = 'hidden';
  }
  function closeModal(id) {
    document.getElementById(id).style.display = 'none';
    document.body.style.overflow = '';
  }

  // Close modals on backdrop click
  ['clModal','ipModal'].forEach(id => {
    document.getElementById(id).addEventListener('click', function(e) {
      if (e.target === this) closeModal(id);
    });
  });

  // ── Cover Letter ──
  function openCoverLetter() {
    const jobDesc = document.getElementById('jobDesc').value.trim();
    const resumeText = lastResumeText;
    if (!jobDesc) return showError('Please paste a job description first.');
    if (!resumeText) return showError('Please analyze your resume first.');

    document.getElementById('clLoading').style.display = 'block';
    document.getElementById('clContent').style.display = 'none';
    document.getElementById('clError').style.display = 'none';
    openModal('clModal');

    const formData = new FormData();
    formData.append('resume_text', resumeText);
    formData.append('job_description', jobDesc);

    fetch('/cover-letter', { method: 'POST', body: formData })
      .then(r => r.json())
      .then(data => {
        document.getElementById('clLoading').style.display = 'none';
        if (data.error) {
          document.getElementById('clError').textContent = data.error;
          document.getElementById('clError').style.display = 'block';
        } else {
          const ta = document.getElementById('clText');
          ta.value = data.cover_letter;
          ta.readOnly = true;
          ta.style.borderColor = '';
          document.getElementById('clContent').style.display = 'block';
        }
      })
      .catch(() => {
        document.getElementById('clLoading').style.display = 'none';
        document.getElementById('clError').textContent = 'Something went wrong. Please try again.';
        document.getElementById('clError').style.display = 'block';
      });
  }

  function closeCoverLetter() { closeModal('clModal'); }

  function copyCoverLetter() {
    navigator.clipboard.writeText(document.getElementById('clText').value).then(() => {
      const btn = document.getElementById('clCopyBtn');
      btn.textContent = '✅ Copied!'; btn.classList.add('copied');
      setTimeout(() => { btn.textContent = '📋 Copy'; btn.classList.remove('copied'); }, 2500);
    });
  }

  function editCoverLetter() {
    const ta = document.getElementById('clText');
    ta.readOnly = false;
    ta.style.borderColor = 'var(--accent)';
    ta.focus();
  }

  function downloadCoverLetterPDF() {
    const text = document.getElementById('clText').value.trim();
    if (!text) return;
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ unit: 'mm', format: 'a4' });
    const pw = 210, margin = 25, usable = pw - margin * 2;
    let y = 20;
    doc.setFillColor(26, 23, 20); doc.rect(0, 0, pw, 22, 'F');
    doc.setFontSize(14); doc.setFont('helvetica', 'bold'); doc.setTextColor(255, 255, 255);
    doc.text('ResumeIQ', margin, 10);
    doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(180, 180, 180);
    doc.text('AI-Generated Cover Letter', margin, 17);
    doc.text(new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' }), pw - margin, 17, { align: 'right' });
    y = 34;
    doc.setFontSize(22); doc.setFont('helvetica', 'bold'); doc.setTextColor(26, 23, 20);
    doc.text('Cover Letter', margin, y); y += 4;
    doc.setDrawColor(45, 106, 79); doc.setLineWidth(0.8);
    doc.line(margin, y, pw - margin, y); y += 10;
    const paragraphs = text.split(/\n\n+/);
    doc.setFontSize(11); doc.setFont('helvetica', 'normal'); doc.setTextColor(40, 40, 40);
    paragraphs.forEach((para, index) => {
      const cleanPara = para.replace(/\n/g, ' ').trim();
      if (!cleanPara) return;
      const lines = doc.splitTextToSize(cleanPara, usable);
      const neededHeight = lines.length * 5.5;
      if (y + neededHeight > 272) { doc.addPage(); y = 20; }
      doc.text(lines, margin, y);
      y += neededHeight + (index < paragraphs.length - 1 ? 6 : 0);
    });
    const pageCount = doc.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setDrawColor(220, 220, 220); doc.setLineWidth(0.3);
      doc.line(margin, 285, pw - margin, 285);
      doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(160, 160, 160);
      doc.text('Generated by ResumeIQ — resumeiq-55h8.onrender.com', margin, 290);
      if (pageCount > 1) doc.text(`Page ${i} of ${pageCount}`, pw - margin, 290, { align: 'right' });
    }
    doc.save('Cover_Letter_ResumeIQ.pdf');
  }

  // ── Interview Prep ──
  function openInterviewPrep() {
    const jobDesc = document.getElementById('jobDesc').value.trim();
    const resumeText = lastResumeText;
    if (!jobDesc) return showError('Please paste a job description first.');
    if (!resumeText) return showError('Please analyze your resume first.');

    document.getElementById('ipLoading').style.display = 'block';
    document.getElementById('ipContent').style.display = 'none';
    document.getElementById('ipContent').innerHTML = '';
    document.getElementById('ipError').style.display = 'none';
    openModal('ipModal');

    const formData = new FormData();
    formData.append('resume_text', resumeText);
    formData.append('job_description', jobDesc);

    fetch('/interview-prep', { method: 'POST', body: formData })
      .then(r => r.json())
      .then(data => {
        document.getElementById('ipLoading').style.display = 'none';
        if (data.error) {
          document.getElementById('ipError').textContent = data.error;
          document.getElementById('ipError').style.display = 'block';
        } else {
          renderInterviewQuestions(data.questions);
        }
      })
      .catch(() => {
        document.getElementById('ipLoading').style.display = 'none';
        document.getElementById('ipError').textContent = 'Something went wrong. Please try again.';
        document.getElementById('ipError').style.display = 'block';
      });
  }

  function renderInterviewQuestions(questions) {
    const container = document.getElementById('ipContent');
    const typeClass = { 'Technical': 'technical', 'Behavioural': 'behavioural', 'Situational': 'situational' };

    container.innerHTML = questions.map((q, i) => {
      const cls = typeClass[q.type] || 'technical';
      return `
        <div class="ip-question-card">
          <div class="ip-q-header">
            <div class="ip-q-num">${i + 1}</div>
            <div class="ip-question">${q.question}</div>
            <div class="ip-q-type ${cls}">${q.type}</div>
          </div>
          <div class="ip-tip-label">💡 How to answer</div>
          <div class="ip-tip">${q.tip}</div>
        </div>`;
    }).join('');

    container.style.display = 'block';
  }

  function closeInterviewPrep() { closeModal('ipModal'); }

  // ── Export Analysis PDF ──
  function exportPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ unit: 'mm', format: 'a4' });
    const pw = 210, margin = 20, usable = pw - margin * 2;
    let y = 20;
    function addText(text, x, startY, maxW, size, style, color) {
      doc.setFontSize(size); doc.setFont('helvetica', style || 'normal');
      if (color) doc.setTextColor(...color); else doc.setTextColor(26, 23, 20);
      const lines = doc.splitTextToSize(String(text), maxW);
      doc.text(lines, x, startY);
      return startY + lines.length * (size * 0.4);
    }
    function checkPage(neededY) { if (neededY > 270) { doc.addPage(); return 20; } return neededY; }
    doc.setFillColor(26, 23, 20); doc.rect(0, 0, pw, 28, 'F');
    doc.setFontSize(20); doc.setFont('helvetica', 'bold'); doc.setTextColor(255, 255, 255);
    doc.text('ResumeIQ', margin, 13);
    doc.setFontSize(9); doc.setFont('helvetica', 'normal'); doc.setTextColor(200, 200, 200);
    doc.text('AI-Powered Resume Analysis Report', margin, 21);
    doc.text(new Date().toLocaleString(), pw - margin, 21, { align: 'right' });
    y = 38;
    const score = parseInt(document.getElementById('scoreNum').textContent) || 0;
    const verdict = document.getElementById('verdictPill').textContent.trim().replace(/[🟢🔵🟡🔴]/g, '').trim();
    const summary = document.getElementById('summary').textContent;
    let scoreColor = score >= 70 ? [45, 106, 79] : score >= 45 ? [199, 123, 47] : [183, 65, 14];
    doc.setFillColor(...scoreColor); doc.roundedRect(margin, y, 36, 36, 5, 5, 'F');
    doc.setFontSize(22); doc.setFont('helvetica', 'bold'); doc.setTextColor(255, 255, 255);
    doc.text(String(score), margin + 18, y + 16, { align: 'center' });
    doc.setFontSize(8); doc.setFont('helvetica', 'normal');
    doc.text('/ 100', margin + 18, y + 24, { align: 'center' });
    doc.setFillColor(...scoreColor.map(c => Math.min(255, c + 160)));
    doc.roundedRect(margin + 42, y, 60, 10, 3, 3, 'F');
    doc.setFontSize(10); doc.setFont('helvetica', 'bold'); doc.setTextColor(...scoreColor);
    doc.text(verdict, margin + 72, y + 7, { align: 'center' });
    y = addText(summary, margin + 42, y + 16, usable - 42, 10, 'normal', [60, 60, 60]);
    y += 8;
    doc.setFillColor(230, 230, 230); doc.roundedRect(margin, y, usable, 5, 2, 2, 'F');
    doc.setFillColor(...scoreColor); doc.roundedRect(margin, y, usable * (score / 100), 5, 2, 2, 'F');
    y += 14;
    function addSection(title, dotColor, content, isTagList) {
      y = checkPage(y + 10);
      doc.setFillColor(...dotColor); doc.circle(margin + 3, y + 3, 2, 'F');
      doc.setFontSize(9); doc.setFont('helvetica', 'bold'); doc.setTextColor(138, 129, 120);
      doc.text(title.toUpperCase(), margin + 8, y + 5); y += 10;
      if (isTagList) {
        let tx = margin; const tagH = 8, tagPad = 4;
        doc.setFontSize(9); doc.setFont('helvetica', 'normal');
        content.forEach(tag => {
          const tw = doc.getTextWidth(tag) + tagPad * 2;
          if (tx + tw > pw - margin) { tx = margin; y += tagH + 3; }
          y = checkPage(y);
          doc.setFillColor(...dotColor.map(c => Math.min(255, c + 150)));
          doc.roundedRect(tx, y - 1, tw, tagH, 2, 2, 'F');
          doc.setTextColor(...dotColor);
          doc.text(tag, tx + tagPad, y + 5); tx += tw + 4;
        });
        y += tagH + 6;
      } else {
        content.forEach(item => {
          y = checkPage(y + 6);
          doc.setFillColor(...dotColor); doc.circle(margin + 3, y + 2, 1.5, 'F');
          y = addText(item, margin + 8, y, usable - 8, 10, 'normal', [40, 40, 40]); y += 2;
        });
        y += 4;
      }
    }
    const matched = [...document.getElementById('matchedKeywords').querySelectorAll('.tag')].map(t => t.textContent);
    const missing = [...document.getElementById('missingKeywords').querySelectorAll('.tag')].map(t => t.textContent);
    const strengths = [...document.getElementById('strengths').querySelectorAll('li')].map(li => li.textContent);
    const improvements = [...document.getElementById('improvements').querySelectorAll('li')].map(li => li.textContent);
    if (matched.length) addSection('Matched Keywords', [45, 106, 79], matched, true);
    if (missing.length) addSection('Missing Keywords', [183, 65, 14], missing, true);
    if (strengths.length) addSection('Strengths', [45, 106, 79], strengths, false);
    if (improvements.length) addSection('Areas to Improve', [199, 123, 47], improvements, false);
    const pageCount = doc.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setDrawColor(220, 220, 220); doc.line(margin, 285, pw - margin, 285);
      doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(160, 160, 160);
      doc.text('Generated by ResumeIQ — resumeiq-55h8.onrender.com', margin, 290);
      doc.text(`Page ${i} of ${pageCount}`, pw - margin, 290, { align: 'right' });
    }
    doc.save('ResumeIQ_Analysis.pdf');
  }

  // ── Score History ──
  const HISTORY_KEY = 'resumeiq_history';
  const MAX_HISTORY = 5;
  function saveToHistory(data, jobDesc) {
    let history = getHistory();
    const entry = {
      score: data.match_score, verdict: data.verdict, summary: data.summary,
      jobDesc: jobDesc.substring(0, 80), matched: data.matched_keywords,
      missing: data.missing_keywords, strengths: data.strengths,
      improvements: data.improvements,
      time: new Date().toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' })
    };
    history.unshift(entry);
    history = history.slice(0, MAX_HISTORY);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    renderHistory();
  }
  function getHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; }
    catch { return []; }
  }
  function clearHistory() { localStorage.removeItem(HISTORY_KEY); renderHistory(); }
  function getScoreColor(score) {
    if (score >= 70) return '#2D6A4F';
    if (score >= 45) return '#C77B2F';
    return '#B7410E';
  }
  function renderHistory() {
    const history = getHistory();
    const section = document.getElementById('historySection');
    const list = document.getElementById('historyList');
    if (!history.length) { section.style.display = 'none'; return; }
    section.style.display = 'block';
    list.innerHTML = history.map((entry, i) => {
      const color = getScoreColor(entry.score);
      return `<div class="history-card" onclick="loadHistoryEntry(${i})">
        <div class="history-score" style="color:${color}">${entry.score}</div>
        <div class="history-meta">
          <div class="history-jd">${entry.jobDesc}…</div>
          <div class="history-time">🕐 ${entry.time}</div>
        </div>
        <div class="history-verdict" style="background:${color}22; color:${color}">${entry.verdict}</div>
      </div>`;
    }).join('');
  }
  function loadHistoryEntry(i) {
    const entry = getHistory()[i];
    if (!entry) return;
    document.getElementById('scoreNum').textContent = entry.score;
    document.getElementById('summary').textContent = entry.summary;
    const pill = document.getElementById('verdictPill');
    pill.className = 'verdict-pill ' + getVerdictClass(entry.verdict);
    pill.textContent = getVerdictEmoji(entry.verdict) + '  ' + entry.verdict;
    document.getElementById('scoreBar').style.width = '0%';
    setTimeout(() => document.getElementById('scoreBar').style.width = entry.score + '%', 100);
    document.getElementById('matchedKeywords').innerHTML = entry.matched.map(k => '<span class="tag matched">' + k + '</span>').join('');
    document.getElementById('missingKeywords').innerHTML = entry.missing.map(k => '<span class="tag missing">' + k + '</span>').join('');
    document.getElementById('strengths').innerHTML = entry.strengths.map(s => '<li>' + s + '</li>').join('');
    document.getElementById('improvements').innerHTML = entry.improvements.map(x => '<li>' + x + '</li>').join('');
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ── Main App ──
  let currentTab = 'upload', selectedFile = null;
let lastResumeText = '';   // stores resume text from last analysis (works for PDF or pasted text)
  function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.tab').forEach((t, i) => t.classList.toggle('active', (i===0&&tab==='upload')||(i===1&&tab==='paste')));
    document.getElementById('uploadTab').style.display = tab === 'upload' ? 'block' : 'none';
    document.getElementById('pasteTab').style.display = tab === 'paste' ? 'block' : 'none';
    if (tab === 'upload') clearHighlights();
  }
  function handleFile(input) {
    const file = input.files[0]; if (!file) return;
    selectedFile = file;
    document.getElementById('fileSelected').style.display = 'flex';
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('dropZone').style.display = 'none';
  }
  function removeFile() {
    selectedFile = null;
    document.getElementById('pdfInput').value = '';
    document.getElementById('fileSelected').style.display = 'none';
    document.getElementById('dropZone').style.display = 'block';
  }
  const dropZone = document.getElementById('dropZone');
  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault(); dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      selectedFile = file;
      document.getElementById('fileSelected').style.display = 'flex';
      document.getElementById('fileName').textContent = file.name;
      dropZone.style.display = 'none';
    }
  });
  function showError(msg) {
    const b = document.getElementById('errorBox');
    b.textContent = msg; b.style.display = 'block';
    setTimeout(() => b.style.display = 'none', 6000);
  }
  function getVerdictClass(v) {
    if (v.includes('Strong')) return 'strong';
    if (v.includes('Good')) return 'good';
    if (v.includes('Partial')) return 'partial';
    return 'weak';
  }
  function getVerdictEmoji(v) {
    if (v.includes('Strong')) return '🟢';
    if (v.includes('Good')) return '🔵';
    if (v.includes('Partial')) return '🟡';
    return '🔴';
  }
  function copyResults() {
    const score = document.getElementById('scoreNum').textContent;
    const verdict = document.getElementById('verdictPill').textContent;
    const summary = document.getElementById('summary').textContent;
    const matched = [...document.getElementById('matchedKeywords').querySelectorAll('.tag')].map(t => t.textContent).join(', ');
    const missing = [...document.getElementById('missingKeywords').querySelectorAll('.tag')].map(t => t.textContent).join(', ');
    const strengths = [...document.getElementById('strengths').querySelectorAll('li')].map(li => '• ' + li.textContent).join('\n');
    const improvements = [...document.getElementById('improvements').querySelectorAll('li')].map(li => '• ' + li.textContent).join('\n');
    const text = ['ResumeIQ Analysis Report', '─────────────────────────',
      `Score     : ${score}/100`, `Verdict   : ${verdict.trim()}`, `Summary   : ${summary}`, '',
      `Matched Keywords: ${matched || 'None'}`, `Missing Keywords: ${missing || 'None'}`, '',
      'Strengths:', strengths, '', 'Areas to Improve:', improvements, '',
      `Generated by ResumeIQ — ${new Date().toLocaleString()}`].join('\n');
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.getElementById('copyBtn');
      btn.textContent = '✅ Copied!'; btn.classList.add('copied');
      setTimeout(() => { btn.textContent = '📋 Copy'; btn.classList.remove('copied'); }, 2500);
    }).catch(() => alert('Could not copy. Please copy manually.'));
  }
  async function analyze() {
    const jobDesc = document.getElementById('jobDesc').value.trim();
    const resumeText = document.getElementById('resumeText').value.trim();
    if (!jobDesc) return showError('Please paste a job description.');
    if (currentTab === 'upload' && !selectedFile) return showError('Please upload a PDF resume.');
    if (currentTab === 'paste' && !resumeText) return showError('Please paste your resume text.');
    const btn = document.getElementById('analyzeBtn');
    btn.classList.add('loading');
    btn.disabled = true;
    document.getElementById('loadingMsg').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('skeletonWrap').classList.add('active');
    document.getElementById('skeletonWrap').scrollIntoView({ behavior: 'smooth', block: 'start' });
    const formData = new FormData();
    formData.append('job_description', jobDesc);
    if (currentTab === 'upload' && selectedFile) formData.append('resume_pdf', selectedFile);
    else formData.append('resume_text', resumeText);
    try {
      const res = await fetch('/analyze', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.error) return showError(data.error);
      document.getElementById('scoreNum').textContent = data.match_score;
      document.getElementById('summary').textContent = data.summary;
      const pill = document.getElementById('verdictPill');
      pill.className = 'verdict-pill ' + getVerdictClass(data.verdict);
      pill.textContent = getVerdictEmoji(data.verdict) + '  ' + data.verdict;
      document.getElementById('scoreBar').style.width = '0%';
      setTimeout(() => document.getElementById('scoreBar').style.width = data.match_score + '%', 100);
      document.getElementById('matchedKeywords').innerHTML = data.matched_keywords.map(k => '<span class="tag matched">' + k + '</span>').join('');
      document.getElementById('missingKeywords').innerHTML = data.missing_keywords.map(k => '<span class="tag missing">' + k + '</span>').join('');
      document.getElementById('strengths').innerHTML = data.strengths.map(s => '<li>' + s + '</li>').join('');
      document.getElementById('improvements').innerHTML = data.improvements.map(i => '<li>' + i + '</li>').join('');
      lastResumeText = data.resume_text || resumeText;
      if (currentTab === 'paste') highlightKeywords(resumeText, data.matched_keywords, data.missing_keywords);
      document.querySelectorAll('.tpl-btn').forEach(b => b.classList.remove('active'));
      saveToHistory(data, jobDesc);
      document.getElementById('results').style.display = 'block';
      document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch(e) {
      showError('Something went wrong. Please try again.');
    } finally {
      btn.classList.remove('loading');
      btn.disabled = false;
      document.getElementById('loadingMsg').style.display = 'none';
      document.getElementById('skeletonWrap').classList.remove('active');
    }
  }
  window.addEventListener('DOMContentLoaded', () => {
    renderHistory();
    initTheme();
  });