import base64
import hashlib

import streamlit as st

from config import BASE_DIR, CONTENT_MAX_LENGTH, HEADLINE_MAX_LENGTH
from services.model_service import load_resources, decide_final_assessment
from services.source_verification import assess_news_url, verify_with_malaysian_sources
from ui.styles import MAIN_CSS
from ui.components import (
    build_result_card_html,
    render_submitted_news_expander,
    render_user_awareness_section,
    render_why_expander,
    render_articles_expander,
    render_advanced_expander,
)
import utils.text_processing as tp

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TruthGuard | AI Fake News Detection",
    page_icon="shield",
    layout="wide",
)
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ── Load ML resources ─────────────────────────────────────────────────────────
model, tfidf, lemmatizer, english_stopwords = load_resources()
tp.init(lemmatizer, english_stopwords)

# ── Hero ──────────────────────────────────────────────────────────────────────
logo_base64 = base64.b64encode((BASE_DIR / "TGLogo.png").read_bytes()).decode()
st.markdown(
    f"""
    <div class="tg-hero">
        <img class="tg-logo" src="data:image/png;base64,{logo_base64}" alt="TruthGuard logo">
        <p class="tg-tagline">AI-Based Fake News Detection System</p>
        <p class="tg-method">Random Forest Classification with Malaysian News Source Verification</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="tg-feature-grid">
        <div class="tg-feature-card">
            <div class="tg-feature-icon">&#x1F9E0;</div>
            <h3>AI Classification</h3>
            <p>Uses Random Forest machine learning to analyze news content patterns.</p>
        </div>
        <div class="tg-feature-card">
            <div class="tg-feature-icon">&#x1F4F0;</div>
            <h3>Malaysian Source Verification</h3>
            <p>Checks trusted Malaysian news sources for supporting evidence.</p>
        </div>
        <div class="tg-feature-card">
            <div class="tg-feature-icon">&#x1F6E1;&#xFE0F;</div>
            <h3>User Awareness</h3>
            <p>Educates users about misinformation risks and provides safe actions before sharing news.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── User guide ────────────────────────────────────────────────────────────────
with st.expander("User Guide / Panduan Pengguna"):
    english_guide, malay_guide = st.tabs(["English", "Bahasa Melayu"])

    with english_guide:
        st.markdown(
            """
            ### How to use TruthGuard

            1. Paste the full **news content** (required) -- at least one complete paragraph.
            2. Add the **headline** if available to improve source verification accuracy.
            3. Add the original **news URL** if available. A trusted URL helps prioritise
               the first search, but does not automatically prove the news is real.
            4. Press **Analyze News** and review the result.

            ### Final assessment labels

            | Label | Meaning |
            |---|---|
            | **Likely Real** | Strong ML signal and/or trusted Malaysian source match |
            | **Likely Fake** | ML detected fake-news patterns without strong source support |
            | **Needs Further Verification** | Evidence is weak, conflicting, or unavailable |

            TruthGuard provides an advisory assessment, not final proof. Always verify the
            original source, publication date, and author before sharing.

            ### Understanding the two indicators

            The result card shows two separate circular indicators.

            - **Model Confidence** -- how certain the Random Forest model is about the
              writing pattern it detected. This is not a truth percentage.
            - **Trusted Source Match** -- how closely a trusted Malaysian article matches
              your submitted text. This is not a truth percentage either.

            The two percentages measure different things and are never combined into a
            single score. Full technical details are inside **"Why did I get this result?"**.

            ### User Awareness & Safe Sharing Guidance

            After the result, a bilingual section provides:

            - **Awareness Message** -- a short explanation of what to remain cautious about
              for your specific result (Likely Real, Likely Fake, or Needs Further Verification).
            - **Safe Actions** -- concise steps to take before sharing the news.

            All guidance is deterministic. No language model is involved.
            """
        )

    with malay_guide:
        st.markdown(
            """
            ### Cara menggunakan TruthGuard

            1. Tampalkan **kandungan berita** penuh (wajib) -- sekurang-kurangnya satu perenggan lengkap.
            2. Masukkan **tajuk berita** jika ada untuk meningkatkan ketepatan pengesahan sumber.
            3. Masukkan **URL asal berita** jika ada. URL daripada sumber dipercayai membantu
               mengutamakan carian, tetapi tidak membuktikan berita itu benar secara automatik.
            4. Tekan **Analyze News** dan semak keputusan.

            ### Label keputusan akhir

            | Label | Maksud |
            |---|---|
            | **Likely Real** | Isyarat ML kukuh dan/atau padanan sumber Malaysia dipercayai |
            | **Likely Fake** | ML mengesan corak berita palsu tanpa sokongan sumber kukuh |
            | **Needs Further Verification** | Bukti lemah, bercanggah, atau tidak tersedia |

            TruthGuard memberikan penilaian sebagai panduan, bukan bukti muktamad. Sentiasa
            semak sumber asal, tarikh penerbitan, dan penulis sebelum berkongsi.

            ### Memahami dua penunjuk

            Kad keputusan menunjukkan dua penunjuk bulat yang berasingan.

            - **Model Confidence** -- sejauh mana model Random Forest yakin dengan corak
              penulisan yang dikesan. Ini bukan peratusan kebenaran.
            - **Trusted Source Match** -- sejauh mana artikel Malaysia dipercayai menyerupai
              teks yang dikemukakan. Ini juga bukan peratusan kebenaran.

            Kedua-dua peratusan mengukur perkara yang berbeza dan tidak pernah digabungkan.
            Butiran teknikal penuh terdapat dalam **"Why did I get this result?"**.

            ### Kesedaran Pengguna & Panduan Perkongsian Selamat

            Selepas keputusan, bahagian dwibahasa menyediakan:

            - **Kesedaran Pengguna** -- penjelasan ringkas tentang perkara yang perlu diberi
              perhatian bagi keputusan anda.
            - **Tindakan Selamat** -- langkah ringkas sebelum berkongsi berita.

            Semua panduan adalah deterministik. Tiada model bahasa digunakan.
            """
        )

# ── Input form — shown only when no valid analysis result exists ───────────────
if "last_analysis" not in st.session_state:
    # Restore any values the user had entered before a validation failure.
    _draft = st.session_state.get("_draft", {})
    _form_errors: list[str] = st.session_state.get("_form_errors", [])

    with st.container(border=True):
        st.markdown('<div class="tg-section-heading">Analyze News</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="tg-section-note">'
            '<b>Quick Guide:</b><br>'
            '1. Paste the news content (required).<br>'
            '2. Add the headline if available for better verification.<br>'
            '3. Add the URL only if you have the original article link.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="margin:12px 0 18px;padding:10px 16px;'
            'background:rgba(0,212,255,.06);border:1px solid rgba(0,212,255,.18);'
            'border-radius:10px;color:#9DB4C8;font-size:.88rem;line-height:1.6;">'
            '<b>Notis Privasi / Privacy Notice:</b> '
            'Kandungan yang dihantar digunakan untuk analisis berita. '
            'Jangan masukkan kata laluan, maklumat peribadi, atau data sulit. '
            'Keputusan sistem ialah panduan dan bukan bukti muktamad. / '
            'Submitted content is used for news analysis. '
            'Do not enter passwords, personal information, or confidential data. '
            'System results are advisory and are not final proof.'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.form("analyze_form"):
            news_content = st.text_area(
                "News Content (required)",
                value=_draft.get("content", ""),
                height=260,
                placeholder="Paste the news content for AI analysis",
                help=f"Paste the full news text or at least one paragraph. Maximum {CONTENT_MAX_LENGTH} characters.",
            )
            news_headline = st.text_input(
                "News Headline (optional, recommended)",
                value=_draft.get("headline", ""),
                placeholder="Enter the news headline",
                help="Add the headline if available. This helps improve source verification.",
            )
            news_url = st.text_input(
                "News URL (optional)",
                value=_draft.get("url", ""),
                placeholder="https://example.com/news-article",
                help="Paste the original article link if available. Must start with http:// or https://",
            )
            analyze_button = st.form_submit_button("Analyze News")

    # Show any validation errors from the previous submit attempt.
    for _err in _form_errors:
        st.error(_err)

    # ── Compute phase ─────────────────────────────────────────────────────────
    if analyze_button:
        # Persist the entered values immediately so they survive a rerun.
        st.session_state["_draft"] = {
            "content": news_content,
            "headline": news_headline,
            "url": news_url,
        }

        errors: list[str] = []
        if not news_content.strip():
            errors.append("Please paste the news content before analysis.")
        elif len(news_content) > CONTENT_MAX_LENGTH:
            errors.append(
                f"News content is too long. Maximum is {CONTENT_MAX_LENGTH:,} characters "
                f"({len(news_content):,} entered)."
            )
        if news_headline and len(news_headline) > HEADLINE_MAX_LENGTH:
            errors.append(
                f"Headline is too long. Maximum is {HEADLINE_MAX_LENGTH} characters."
            )
        if news_url and not news_url.strip().startswith(("http://", "https://")):
            errors.append("Please enter a valid URL starting with http:// or https://")

        if errors:
            # Save errors and rerun so the form re-renders with the draft values intact.
            st.session_state["_form_errors"] = errors
            st.rerun()

        # Validation passed — clear error state and run analysis.
        st.session_state.pop("_form_errors", None)

        language_code, language_name = tp.detect_input_language(news_content)
        translated_text = None
        if language_code == "ms":
            with st.spinner("Translating Malay text for the English-trained model..."):
                translated_text = tp.translate_malay_to_english(news_content)

        prediction_text = translated_text or news_content
        cleaned_text = tp.clean_text(prediction_text)
        vectorized_text = tfidf.transform([cleaned_text])
        prediction = model.predict(vectorized_text)[0]
        probabilities = model.predict_proba(vectorized_text)[0]
        confidence = max(probabilities) * 100

        url_status = assess_news_url(news_url)
        trusted_url_hint = url_status["domain"] if url_status["trusted"] else None
        verification_content = f"{news_content} {translated_text or ''}".strip()
        with st.spinner("Searching trusted Malaysian sources..."):
            verification = verify_with_malaysian_sources(
                news_headline,
                verification_content,
                trusted_url_hint,
            )

        decision = decide_final_assessment(prediction, confidence, verification["status"])
        final_label = decision["label"]
        analysis_id = hashlib.md5(
            f"{news_headline}|{news_content[:500]}|{final_label}".encode()
        ).hexdigest()[:16]

        # Draft no longer needed — the submitted values are stored in last_analysis.
        st.session_state.pop("_draft", None)

        st.session_state["last_analysis"] = {
            "news_headline": news_headline,
            "news_url": news_url,
            "news_content": news_content,
            "language_code": language_code,
            "language_name": language_name,
            "translated_text": translated_text,
            "cleaned_text": cleaned_text,
            "prediction": prediction,
            "probabilities": list(probabilities),
            "confidence": confidence,
            "url_status": url_status,
            "verification": verification,
            "matched_articles": verification["matched_articles"],
            "decision": decision,
            "final_label": final_label,
            "analysis_id": analysis_id,
        }
        st.rerun()

# ── Result phase — rendered from session state, survives all reruns ────────────
if "last_analysis" in st.session_state:
    _a = st.session_state["last_analysis"]
    news_headline    = _a["news_headline"]
    news_url         = _a["news_url"]
    news_content     = _a["news_content"]
    language_code    = _a["language_code"]
    language_name    = _a["language_name"]
    translated_text  = _a["translated_text"]
    cleaned_text     = _a["cleaned_text"]
    prediction       = _a["prediction"]
    probabilities    = _a["probabilities"]
    confidence       = _a["confidence"]
    url_status       = _a["url_status"]
    verification     = _a["verification"]
    matched_articles = _a["matched_articles"]
    decision         = _a["decision"]
    final_label      = _a["final_label"]

    label_colors = {
        "Likely Real": "#16a34a",
        "Likely Fake": "#dc2626",
        "Needs Further Verification": "#d97706",
    }
    result_styles = {
        "Likely Real": {
            "icon": "&#10003;",
            "background": "linear-gradient(135deg, rgba(13,110,75,.96), rgba(21,160,103,.82))",
        },
        "Likely Fake": {
            "icon": "&#9888;",
            "background": "linear-gradient(135deg, rgba(153,27,27,.96), rgba(220,38,38,.82))",
        },
        "Needs Further Verification": {
            "icon": "&#8981;",
            "background": "linear-gradient(135deg, rgba(154,76,0,.96), rgba(217,119,6,.84))",
        },
    }
    user_explanations = {
        "Likely Real": (
            "The system found strong support from the ML model and/or trusted "
            "Malaysian sources."
        ),
        "Likely Fake": (
            "The system detected patterns commonly found in fake news and did not "
            "find strong trusted source support."
        ),
        "Needs Further Verification": (
            "The system could not find enough evidence to make a strong decision. "
            "Please verify with official sources before sharing."
        ),
    }

    # 1. View Submitted News (collapsed by default)
    render_submitted_news_expander(news_headline, news_url, news_content)

    # 2. Final Assessment Card
    st.markdown(
        build_result_card_html(
            final_label,
            result_styles[final_label],
            user_explanations[final_label],
            decision,
            confidence,
            verification["status"],
            verification["highest_similarity"],
        ),
        unsafe_allow_html=True,
    )

    # 3. User Awareness & Safe Sharing Guidance
    render_user_awareness_section(final_label, label_colors[final_label])

    # 4. Check Another News — secondary style so result stays visually primary
    if st.button("Check Another News", key="reset_btn", type="secondary"):
        for _k in list(st.session_state.keys()):
            st.session_state.pop(_k, None)
        st.rerun()

    # 5. Why did I get this result?
    render_why_expander(decision, confidence, verification, url_status, probabilities, model)

    # 6. Related Trusted Articles
    render_articles_expander(matched_articles)

    # 7. Advanced Technical Details
    render_advanced_expander(
        language_name, language_code, news_content,
        translated_text, cleaned_text, verification,
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="tg-proof-note">
        This system provides AI-assisted checking and source verification. It should not
        be treated as final proof.
    </div>
    <div class="footer">
        <b>TruthGuard v1.0</b><br>
        Developed by IAIMAN ILYAS BIN AZMI<br>
        Final Year Project<br>
        University College TATI
    </div>
    """,
    unsafe_allow_html=True,
)
