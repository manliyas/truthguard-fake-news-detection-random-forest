"""
Core unit tests — run with: python -m pytest tests/
No ML models or network access required.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.source_verification import get_domain, is_trusted_malaysian_domain, assess_news_url


# ── URL / domain helpers ──────────────────────────────────────────────────────

def test_get_domain_strips_www():
    assert get_domain("https://www.thestar.com.my/news") == "thestar.com.my"


def test_get_domain_no_scheme():
    assert get_domain("nst.com.my/article") == "nst.com.my"


def test_get_domain_empty():
    assert get_domain("") == ""


def test_trusted_domain_direct():
    assert is_trusted_malaysian_domain("https://bernama.com/en/news.php?id=1") is True


def test_trusted_domain_subdomain():
    assert is_trusted_malaysian_domain("https://berita.rtm.gov.my/article") is True


def test_untrusted_domain():
    assert is_trusted_malaysian_domain("https://example.com/news") is False


def test_assess_news_url_empty():
    result = assess_news_url("")
    assert result == {"provided": False, "domain": "", "trusted": False}


def test_assess_news_url_trusted():
    result = assess_news_url("https://astroawani.com/berita-malaysia/article")
    assert result["provided"] is True
    assert result["trusted"] is True


def test_assess_news_url_untrusted():
    result = assess_news_url("https://unknownnews.net/article")
    assert result["provided"] is True
    assert result["trusted"] is False


# ── Decision rules ────────────────────────────────────────────────────────────

from services.model_service import decide_final_assessment


def test_high_confidence_real():
    result = decide_final_assessment(0, 95.0, "no_match")
    assert result["label"] == "Likely Real"
    assert result["confidence_category"] == "High"


def test_high_confidence_fake():
    result = decide_final_assessment(1, 92.0, "strong_match")
    assert result["label"] == "Likely Fake"


def test_moderate_real_strong_match():
    result = decide_final_assessment(0, 75.0, "strong_match")
    assert result["label"] == "Likely Real"


def test_moderate_fake_no_match():
    result = decide_final_assessment(1, 70.0, "no_match")
    assert result["label"] == "Likely Fake"


def test_moderate_unavailable():
    result = decide_final_assessment(0, 65.0, "no_articles")
    assert result["label"] == "Needs Further Verification"


def test_moderate_possible_match():
    result = decide_final_assessment(0, 70.0, "possible_match")
    assert result["label"] == "Needs Further Verification"


def test_low_strong_match():
    result = decide_final_assessment(1, 50.0, "strong_match")
    assert result["label"] == "Likely Real"


def test_low_no_match():
    result = decide_final_assessment(1, 50.0, "no_match")
    assert result["label"] == "Needs Further Verification"


def test_low_fake_never_likely_fake():
    result = decide_final_assessment(1, 55.0, "no_match")
    assert result["label"] != "Likely Fake"


# ── Similarity formula ────────────────────────────────────────────────────────

def test_weighted_similarity_formula():
    headline_sim = 0.20
    content_sim = 0.10
    expected = (headline_sim * 0.70) + (content_sim * 0.30)
    assert abs(expected - 0.17) < 1e-9


def test_weighted_similarity_headline_dominant():
    headline_sim = 0.30
    content_sim = 0.00
    result = (headline_sim * 0.70) + (content_sim * 0.30)
    assert result == 0.21
