import joblib
import nltk
import streamlit as st
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from config import BASE_DIR, STRONG_MATCH_THRESHOLD, POSSIBLE_MATCH_THRESHOLD


@st.cache_resource
def load_resources():
    for resource, package in [
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]:
        try:
            nltk.data.find(resource)
        except LookupError:
            try:
                nltk.data.find(f"{resource}.zip")
            except LookupError:
                nltk.download(package, quiet=True)

    saved_model = joblib.load(BASE_DIR / "random_forest_model.pkl")
    saved_model.n_jobs = 1
    saved_tfidf = joblib.load(BASE_DIR / "tfidf_vectorizer.pkl")
    return saved_model, saved_tfidf, WordNetLemmatizer(), set(stopwords.words("english"))


def decide_final_assessment(prediction: int, confidence: float, verification_status: str) -> dict:
    strong_match = verification_status == "strong_match"
    possible_match = verification_status == "possible_match"
    external_unavailable = verification_status in {"search_failed", "no_articles"}

    if confidence >= 90:
        confidence_category = "High"
    elif confidence >= 60:
        confidence_category = "Moderate"
    else:
        confidence_category = "Low"

    prediction_label = "Real-news pattern" if prediction == 0 else "Fake-news pattern"

    _verification_map = {
        "strong_match": "Strong Match",
        "possible_match": "Possible Match",
        "no_match": "No Match",
        "no_articles": "No Related Articles",
        "search_failed": "Search Unavailable",
    }
    verification_category = _verification_map.get(verification_status, "Unknown")

    if confidence >= 90:
        if prediction == 0:
            label, color = "Likely Real", "#16a34a"
            explanation = (
                "The high-confidence ML prediction is primary; "
                "external verification is supporting evidence only."
            )
            applied_rule = "High-confidence Real prediction"
            rule_explanation = (
                f"Random Forest detected a Real-news pattern with {confidence:.2f}% confidence, "
                f"which is High confidence. At high confidence the ML prediction is primary and "
                f"source verification is supporting evidence only. "
                f"The final assessment is Likely Real."
            )
        else:
            label, color = "Likely Fake", "#dc2626"
            explanation = (
                "The high-confidence ML prediction is primary; "
                "external verification is supporting evidence only."
            )
            applied_rule = "High-confidence Fake prediction"
            rule_explanation = (
                f"Random Forest detected a Fake-news pattern with {confidence:.2f}% confidence, "
                f"which is High confidence. At high confidence the ML prediction is primary and "
                f"source verification is supporting evidence only. "
                f"The final assessment is Likely Fake."
            )

    elif confidence >= 60:
        if external_unavailable:
            label, color = "Needs Further Verification", "#d97706"
            explanation = "The ML confidence is moderate and external verification is unavailable."
            applied_rule = "Moderate confidence with unavailable verification"
            rule_explanation = (
                f"Random Forest detected a {prediction_label} with {confidence:.2f}% confidence, "
                f"which is Moderate confidence. External source verification was unavailable. "
                f"Based on the rule for moderate confidence with unavailable verification, "
                f"the final assessment is Needs Further Verification."
            )
        elif possible_match:
            label, color = "Needs Further Verification", "#d97706"
            explanation = (
                "A possible trusted Malaysian source match was found, "
                "but it is below the strong-match threshold."
            )
            applied_rule = "Moderate confidence with possible (not strong) source match"
            rule_explanation = (
                f"Random Forest detected a {prediction_label} with {confidence:.2f}% confidence, "
                f"which is Moderate confidence. A possible trusted-source match was found, "
                f"but it is below the {STRONG_MATCH_THRESHOLD:.0%} strong-match threshold. "
                f"The final assessment is Needs Further Verification."
            )
        elif prediction == 0 and strong_match:
            label, color = "Likely Real", "#16a34a"
            explanation = "The ML prediction is supported by a similar trusted Malaysian report."
            applied_rule = "Moderate Real prediction with strong source match"
            rule_explanation = (
                f"Random Forest detected a Real-news pattern with {confidence:.2f}% confidence, "
                f"which is Moderate confidence. A strong trusted-source match was found "
                f"(similarity >= {STRONG_MATCH_THRESHOLD:.0%}). "
                f"Based on the rule for a moderate-confidence Real prediction with strong "
                f"trusted-source support, the final assessment is Likely Real."
            )
        elif prediction == 1 and not strong_match:
            label, color = "Likely Fake", "#dc2626"
            explanation = "The ML prediction is not supported by a similar trusted Malaysian report."
            applied_rule = "Moderate Fake prediction without strong trusted-source support"
            rule_explanation = (
                f"Random Forest detected a Fake-news pattern with {confidence:.2f}% confidence, "
                f"which is Moderate confidence. The highest trusted-source similarity was "
                f"{verification_category.lower()} (below the {STRONG_MATCH_THRESHOLD:.0%} strong-match threshold). "
                f"Based on the rule for a moderate-confidence Fake prediction without strong "
                f"trusted-source support, the final assessment is Likely Fake."
            )
        else:
            label, color = "Needs Further Verification", "#d97706"
            explanation = "The ML prediction and Malaysian source verification conflict."
            applied_rule = "Moderate confidence with conflicting ML and source evidence"
            rule_explanation = (
                f"Random Forest detected a {prediction_label} with {confidence:.2f}% confidence, "
                f"which is Moderate confidence. The ML prediction and trusted-source verification "
                f"conflict. The final assessment is Needs Further Verification."
            )

    elif strong_match:
        label, color = "Likely Real", "#16a34a"
        explanation = "The ML prediction is weak, but a similar trusted Malaysian report was found."
        applied_rule = "Low confidence with strong source match"
        rule_explanation = (
            f"Random Forest detected a {prediction_label} with {confidence:.2f}% confidence, "
            f"which is Low confidence. A strong trusted-source match was found "
            f"(similarity >= {STRONG_MATCH_THRESHOLD:.0%}). "
            f"Low-confidence predictions can only become Likely Real with strong source support. "
            f"The final assessment is Likely Real."
        )
    else:
        label, color = "Needs Further Verification", "#d97706"
        explanation = "The ML prediction is weak and no trusted Malaysian source match was found."
        applied_rule = "Low confidence without strong source match"
        rule_explanation = (
            f"Random Forest detected a {prediction_label} with {confidence:.2f}% confidence, "
            f"which is Low confidence. No strong trusted-source match was found. "
            f"Low-confidence predictions are not classified as Likely Fake; "
            f"therefore, the final assessment is Needs Further Verification."
        )

    return {
        "label": label,
        "color": color,
        "explanation": explanation,
        "confidence_category": confidence_category,
        "applied_rule": applied_rule,
        "rule_explanation": rule_explanation,
        "decision_path": {
            "prediction_label": prediction_label,
            "confidence": confidence,
            "confidence_category": confidence_category,
            "verification_category": verification_category,
            "applied_rule": applied_rule,
            "final_label": label,
        },
    }
