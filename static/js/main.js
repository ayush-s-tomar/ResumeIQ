// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const target = tab.dataset.tab;
    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById('tab-' + target).classList.remove('hidden');
  });
});

// File upload
const dropZone = document.getElementById('dropZone');
const pdfInput = document.getElementById('pdfInput');
const fileSelected = document.getElementById('fileSelected');
const fileName = document.getElementById('fileName');
const removeFile = document.getElementById('removeFile');
let selectedFile = null;

dropZone.addEventListener('click', () => pdfInput.click());

dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file && file.type === 'application/pdf') setFile(file);
});

pdfInput.addEventListener('change', () => {
  if (pdfInput.files[0]) setFile(pdfInput.files[0]);
});

function setFile(file) {
  selectedFile = file;
  fileName.textContent = file.name;
  dropZone.style.display = 'none';
  fileSelected.style.display = 'flex';
}

removeFile.addEventListener('click', () => {
  selectedFile = null;
  pdfInput.value = '';
  dropZone.style.display = 'block';
  fileSelected.style.display = 'none';
});

// Loader messages
const loaderMessages = [
  'Scanning your resume...',
  'Matching keywords...',
  'Identifying gaps...',
  'Generating insights...'
];
let loaderInterval;

function startLoader() {
  let i = 0;
  document.getElementById('loaderText').textContent = loaderMessages[0];
  loaderInterval = setInterval(() => {
    i = (i + 1) % loaderMessages.length;
    document.getElementById('loaderText').textContent = loaderMessages[i];
  }, 1800);
}
function stopLoader() { clearInterval(loaderInterval); }

// Main analyze
document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const jobDesc = document.getElementById('jobDescription').value.trim();
  const resumeTextarea = document.getElementById('resumeText').value.trim();
  const activeTab = document.querySelector('.tab.active').dataset.tab;

  // Validation
  hideError();
  if (!jobDesc) { showError('Please paste the job description.'); return; }
  if (activeTab === 'upload' && !selectedFile) { showError('Please upload a PDF resume.'); return; }
  if (activeTab === 'paste' && !resumeTextarea) { showError('Please paste your resume text.'); return; }

  // Build form data
  const formData = new FormData();
  formData.append('job_description', jobDesc);
  if (activeTab === 'upload' && selectedFile) {
    formData.append('resume_pdf', selectedFile);
  } else {
    formData.append('resume_text', resumeTextarea);
  }

  // UI state
  setLoading(true);
  document.getElementById('results').classList.add('hidden');

  try {
    const res = await fetch('/analyze', { method: 'POST', body: formData });
    const data = await res.json();

    if (!res.ok || data.error) {
      showError(data.error || 'Something went wrong. Please try again.');
      return;
    }
    renderResults(data);
  } catch (err) {
    showError('Network error. Please check your connection and try again.');
  } finally {
    setLoading(false);
  }
});

function setLoading(loading) {
  const btn = document.getElementById('analyzeBtn');
  const loader = document.getElementById('loader');
  btn.disabled = loading;
  btn.querySelector('.btn-text').textContent = loading ? 'Analyzing...' : 'Analyze Match';
  if (loading) {
    loader.classList.remove('hidden');
    startLoader();
  } else {
    loader.classList.add('hidden');
    stopLoader();
  }
}

function showError(msg) {
  const box = document.getElementById('errorBox');
  document.getElementById('errorMsg').textContent = msg;
  box.classList.remove('hidden');
  box.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
function hideError() {
  document.getElementById('errorBox').classList.add('hidden');
}

function renderResults(data) {
  // Score ring animation
  const score = Math.min(100, Math.max(0, data.match_score || 0));
  const circumference = 326.7;
  const offset = circumference - (score / 100) * circumference;
  const ring = document.getElementById('ringFill');
  const numEl = document.getElementById('scoreNumber');

  // Color ring based on score
  if (score >= 70) ring.style.stroke = '#39d98a';
  else if (score >= 45) ring.style.stroke = '#ffad5e';
  else ring.style.stroke = '#ff6b6b';

  setTimeout(() => { ring.style.strokeDashoffset = offset; }, 100);

  // Animate number
  let current = 0;
  const step = score / 40;
  const counter = setInterval(() => {
    current = Math.min(current + step, score);
    numEl.textContent = Math.floor(current);
    if (current >= score) clearInterval(counter);
  }, 25);

  // Verdict
  document.getElementById('verdictBadge').textContent = data.verdict || '—';
  document.getElementById('summaryText').textContent = data.summary || '';

  // Tags
  renderTags('matchedTags', data.matched_keywords || [], 'tag-green');
  renderTags('missingTags', data.missing_keywords || [], 'tag-red');

  // Lists
  renderList('strengthsList', data.strengths || []);
  renderList('improvementsList', data.improvements || []);

  // Show results
  const resultsEl = document.getElementById('results');
  resultsEl.classList.remove('hidden');
  resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderTags(containerId, items, cls) {
  const el = document.getElementById(containerId);
  el.innerHTML = '';
  if (!items.length) {
    el.innerHTML = '<span style="color:var(--muted);font-size:0.78rem">None found</span>';
    return;
  }
  items.forEach(item => {
    const tag = document.createElement('span');
    tag.className = `tag ${cls}`;
    tag.textContent = item;
    el.appendChild(tag);
  });
}

function renderList(containerId, items) {
  const el = document.getElementById(containerId);
  el.innerHTML = '';
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    el.appendChild(li);
  });
}

// Retry button
document.getElementById('retryBtn').addEventListener('click', () => {
  document.getElementById('results').classList.add('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
