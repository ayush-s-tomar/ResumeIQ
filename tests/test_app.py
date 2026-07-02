import json
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

os.environ.setdefault("GROQ_API_KEY", "test-key-for-ci")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.limiter.enabled = False
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def clear_cache():
    app_module.CACHE.clear()
    yield
    app_module.CACHE.clear()


SAMPLE_RESUME = "Experienced Python developer with 5 years building REST APIs using Flask. " * 3
SAMPLE_JD = "We are looking for a Python developer with Flask experience to join our team."


def mock_groq_response(content):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content=content))]
    return mock_resp


class TestIndexRoute:
    def test_index_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200


class TestAnalyzeValidation:
    def test_missing_job_description_returns_400(self, client):
        res = client.post("/analyze", data={"resume_text": SAMPLE_RESUME})
        assert res.status_code == 400
        assert "Job description" in res.get_json()["error"]

    def test_jd_too_short_returns_400(self, client):
        res = client.post("/analyze", data={
            "job_description": "short",
            "resume_text": SAMPLE_RESUME,
        })
        assert res.status_code == 400

    def test_missing_resume_returns_400(self, client):
        res = client.post("/analyze", data={"job_description": SAMPLE_JD})
        assert res.status_code == 400
        assert "resume" in res.get_json()["error"].lower()

    def test_resume_too_short_returns_400(self, client):
        res = client.post("/analyze", data={
            "job_description": SAMPLE_JD,
            "resume_text": "too short",
        })
        assert res.status_code == 400

    @patch("app.client")
    def test_valid_analysis_returns_200(self, mock_groq, client):
        mock_groq.chat.completions.create.return_value = mock_groq_response(json.dumps({
            "match_score": 80,
            "summary": "Good match overall.",
            "matched_keywords": ["Python", "Flask"],
            "missing_keywords": ["Docker"],
            "strengths": ["Strong backend skills"],
            "improvements": ["Add Docker experience"],
            "verdict": "Good Match"
        }))
        res = client.post("/analyze", data={
            "job_description": SAMPLE_JD,
            "resume_text": SAMPLE_RESUME,
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["match_score"] == 80
        assert data["verdict"] == "Good Match"

    @patch("app.client")
    def test_repeated_request_uses_cache(self, mock_groq, client):
        mock_groq.chat.completions.create.return_value = mock_groq_response(json.dumps({
            "match_score": 75, "summary": "ok", "matched_keywords": [],
            "missing_keywords": [], "strengths": [], "improvements": [],
            "verdict": "Good Match"
        }))
        payload = {"job_description": SAMPLE_JD, "resume_text": SAMPLE_RESUME}
        first = client.post("/analyze", data=payload)
        second = client.post("/analyze", data=payload)
        assert first.status_code == 200
        assert second.status_code == 200
        assert mock_groq.chat.completions.create.call_count == 1


class TestCoverLetterValidation:
    def test_missing_fields_returns_400(self, client):
        res = client.post("/cover-letter", data={})
        assert res.status_code == 400

    @patch("app.client")
    def test_valid_request_returns_200(self, mock_groq, client):
        mock_groq.chat.completions.create.return_value = mock_groq_response(
            "Dear Hiring Manager, I am excited to apply..."
        )
        res = client.post("/cover-letter", data={
            "resume_text": SAMPLE_RESUME,
            "job_description": SAMPLE_JD,
        })
        assert res.status_code == 200
        assert "cover_letter" in res.get_json()


class TestInterviewPrepValidation:
    def test_missing_fields_returns_400(self, client):
        res = client.post("/interview-prep", data={})
        assert res.status_code == 400

    @patch("app.client")
    def test_valid_request_returns_200(self, mock_groq, client):
        mock_groq.chat.completions.create.return_value = mock_groq_response(json.dumps([
            {"question": "Tell me about a Flask project.", "type": "Technical",
             "tip": "Focus on architecture decisions."}
        ]))
        res = client.post("/interview-prep", data={
            "resume_text": SAMPLE_RESUME,
            "job_description": SAMPLE_JD,
        })
        assert res.status_code == 200
        assert len(res.get_json()["questions"]) == 1


class TestHelperFunctions:
    def test_allowed_file_accepts_pdf(self):
        assert app_module.allowed_file("resume.pdf") is True

    def test_allowed_file_rejects_other_types(self):
        assert app_module.allowed_file("resume.docx") is False
        assert app_module.allowed_file("malware.exe") is False

    def test_validate_text_length_too_short(self):
        error = app_module.validate_text_length("hi", 10, 100, "Test field")
        assert error is not None
        assert "too short" in error

    def test_validate_text_length_too_long(self):
        error = app_module.validate_text_length("x" * 200, 10, 100, "Test field")
        assert error is not None
        assert "too long" in error

    def test_validate_text_length_valid(self):
        error = app_module.validate_text_length("x" * 50, 10, 100, "Test field")
        assert error is None

    def test_make_cache_key_is_deterministic(self):
        key1 = app_module.make_cache_key("analyze", "resume text", "jd text")
        key2 = app_module.make_cache_key("analyze", "resume text", "jd text")
        assert key1 == key2

    def test_make_cache_key_differs_for_different_input(self):
        key1 = app_module.make_cache_key("analyze", "resume A", "jd text")
        key2 = app_module.make_cache_key("analyze", "resume B", "jd text")
        assert key1 != key2