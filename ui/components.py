import html

import streamlit as st

from config import STRONG_MATCH_THRESHOLD, POSSIBLE_MATCH_THRESHOLD

_CIRCLE_CIRC = 301.593  # 2 * pi * 48


_AWARENESS_MESSAGES = {
    "Likely Real": {
        "ms": (
            "Berita ini kelihatan lebih boleh dipercayai berdasarkan analisis sistem. "
            "Walau bagaimanapun, walaupun sumber yang dipercayai boleh disalah petik, "
            "laporan yang sudah lapuk boleh digunakan semula, atau kandungan boleh diedit "
            "dan diambil di luar konteks. Sentiasa semak sumber asal sebelum berkongsi."
        ),
        "en": (
            "This news appears more reliable based on the system's analysis. "
            "However, even trusted sources can be misquoted, outdated reports can be "
            "recycled, and content can be edited or taken out of context. "
            "Always verify the original source before sharing."
        ),
    },
    "Likely Fake": {
        "ms": (
            "Berita ini menunjukkan corak yang biasa ditemui dalam berita palsu. "
            "Tanda amaran biasa termasuk: bahasa yang sensasi atau menakutkan, tekanan "
            "emosi untuk berkongsi dengan segera, dakwaan tanpa bukti atau sumber yang "
            "boleh disahkan, dan tajuk yang keterlaluan atau tidak sepadan dengan kandungan. "
            "Berhenti sejenak dan semak sebelum berkongsi."
        ),
        "en": (
            "This news shows patterns commonly found in fake or misleading content. "
            "Common warning signs include: sensational or alarming language, emotional "
            "pressure to share immediately, unsupported claims without verifiable sources, "
            "and exaggerated headlines that do not match the content. "
            "Pause and verify before sharing."
        ),
    },
    "Needs Further Verification": {
        "ms": (
            "Sistem tidak mempunyai bukti yang mencukupi untuk membuat keputusan yang kukuh. "
            "Ini tidak bermakna berita itu benar atau palsu secara automatik — ia bermakna "
            "pengesahan lanjut diperlukan. Bukti yang tidak mencukupi boleh berlaku apabila "
            "berita sangat baru, melibatkan topik khusus, atau tidak diliputi oleh sumber "
            "Malaysia dipercayai yang diindeks. Semak secara manual sebelum berkongsi."
        ),
        "en": (
            "The system does not have enough evidence to make a strong decision. "
            "This does not automatically mean the news is true or false — it means "
            "further verification is required. Insufficient evidence can occur when "
            "the news is very recent, covers a niche topic, or has not been reported "
            "by indexed trusted Malaysian sources. Verify manually before sharing."
        ),
    },
}

_SAFE_ACTIONS = {
    "Likely Real": {
        "ms": [
            "Semak sumber asal berita dan pastikan pautan adalah sahih.",
            "Sahkan tarikh penerbitan — laporan lama kadang-kadang dikongsikan semula sebagai berita baru.",
            "Pastikan nama penulis atau agensi berita disebutkan dengan jelas.",
            "Bandingkan dengan sekurang-kurangnya satu portal berita dipercayai yang lain.",
            "Elakkan berkongsi versi yang telah diedit, dipotong, atau diambil di luar konteks.",
        ],
        "en": [
            "Check the original source and confirm the link is authentic.",
            "Verify the publication date — old reports are sometimes reshared as new news.",
            "Ensure the author or news agency is clearly credited.",
            "Compare with at least one other trusted news portal.",
            "Avoid sharing edited, cropped, or out-of-context versions of the article.",
        ],
    },
    "Likely Fake": {
        "ms": [
            "Jangan kongsi berita ini sehingga anda mengesahkannya daripada sumber rasmi.",
            "Semak dakwaan tersebut di laman web berita dipercayai seperti Bernama, RTM, atau The Star.",
            "Cari tajuk berita yang sama menggunakan enjin carian untuk melihat sama ada ia dilaporkan secara meluas.",
            "Berhati-hati dengan bahasa yang emosional, sensasi, atau mendesak untuk bertindak segera.",
            "Laporkan kandungan yang mengelirukan kepada platform media sosial jika ia boleh menyebabkan kemudaratan.",
        ],
        "en": [
            "Do not share this news until you have verified it from an official source.",
            "Check the claim on trusted news sites such as Bernama, RTM, or The Star.",
            "Search the same headline to see whether it has been widely reported.",
            "Be cautious of emotional, sensational, or urgent language pressuring immediate action.",
            "Report misleading content to the social media platform if it may cause harm.",
        ],
    },
    "Needs Further Verification": {
        "ms": [
            "Bandingkan berita ini dengan sumber Malaysia dipercayai seperti Bernama, RTM, The Star, atau NST.",
            "Semak tarikh, nama penulis, dan URL sumber asal berita.",
            "Cari tajuk yang sama daripada beberapa portal berita yang berbeza.",
            "Semak laman pengesahan fakta seperti Sebenarnya.my atau Jom Check.",
            "Jangan kongsi sehingga anda menemui pengesahan yang kukuh daripada sumber dipercayai.",
        ],
        "en": [
            "Compare this news with trusted Malaysian sources such as Bernama, RTM, The Star, or NST.",
            "Check the date, author name, and original source URL.",
            "Search for the same headline across multiple different news portals.",
            "Check fact-checking sites such as Sebenarnya.my or Jom Check.",
            "Do not share until you find solid confirmation from a trusted source.",
        ],
    },
}


def _decision_basis_text(decision: dict, confidence: float) -> str:
    conf_pct = f"{confidence:.1f}%"
    texts = {
        "High-confidence Real prediction": (
            f"The Random Forest model identified a Real-news writing pattern with high confidence ({conf_pct})."
        ),
        "High-confidence Fake prediction": (
            f"The Random Forest model identified a Fake-news writing pattern with high confidence ({conf_pct})."
        ),
        "Moderate Real prediction with strong source match": (
            f"The Random Forest model detected a Real-news pattern ({conf_pct} confidence), "
            "supported by a trusted Malaysian source match."
        ),
        "Moderate Fake prediction without strong trusted-source support": (
            f"The Random Forest model detected a Fake-news pattern ({conf_pct} confidence) "
            "with no strong trusted-source match found."
        ),
        "Moderate confidence with unavailable verification": (
            f"The Random Forest model's confidence is moderate ({conf_pct}); "
            "source verification was unavailable."
        ),
        "Moderate confidence with possible (not strong) source match": (
            f"The Random Forest model's confidence is moderate ({conf_pct}); "
            "source similarity is below the strong-match threshold."
        ),
        "Moderate confidence with conflicting ML and source evidence": (
            f"The Random Forest model's prediction and source evidence conflict "
            f"at moderate confidence ({conf_pct})."
        ),
        "Low confidence with strong source match": (
            f"The Random Forest model's confidence is low ({conf_pct}), "
            "but a similar report was found from a trusted Malaysian source."
        ),
        "Low confidence without strong source match": (
            "The Random Forest model's confidence is low and no strong trusted-source match was found."
        ),
    }
    return texts.get(decision["applied_rule"], decision["explanation"])


def build_result_card_html(
    final_label: str,
    result_style: dict,
    user_explanation: str,
    decision: dict,
    confidence: float,
    verification_status: str,
    highest_similarity: float,
) -> str:
    ml_offset = _CIRCLE_CIRC * (1.0 - min(confidence, 100.0) / 100.0)
    ml_arc = (
        f'<circle cx="60" cy="60" r="48" fill="none" stroke-width="10" stroke-linecap="round" '
        f'style="stroke:#00D4FF;stroke-dasharray:{_CIRCLE_CIRC:.2f};'
        f'stroke-dashoffset:{ml_offset:.2f};"/>'
    )
    pred_label = decision["decision_path"]["prediction_label"]
    conf_cat = decision["confidence_category"]
    conf_display = f"{confidence:.1f}%"

    source_unavailable = verification_status in {"search_failed", "no_articles"}
    src_cat = decision["decision_path"]["verification_category"]
    if source_unavailable:
        src_display = "N/A"
        src_arc = (
            '<circle cx="60" cy="60" r="48" fill="none" stroke="rgba(255,255,255,0.22)" '
            'stroke-width="8" stroke-dasharray="6 5"/>'
        )
    else:
        src_pct = highest_similarity * 100.0
        src_display = f"{src_pct:.1f}%"
        src_color = {
            "strong_match": "#22c55e",
            "possible_match": "#f59e0b",
        }.get(verification_status, "#64748b")
        src_offset = _CIRCLE_CIRC * (1.0 - min(src_pct, 100.0) / 100.0)
        src_arc = (
            f'<circle cx="60" cy="60" r="48" fill="none" stroke-width="10" stroke-linecap="round" '
            f'style="stroke:{src_color};stroke-dasharray:{_CIRCLE_CIRC:.2f};'
            f'stroke-dashoffset:{src_offset:.2f};"/>'
        )

    basis = _decision_basis_text(decision, confidence)
    _svg_attrs = (
        'viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" '
        'style="transform:rotate(-90deg);width:100px;height:100px;'
        'display:block;position:absolute;top:0;left:0;"'
    )
    _bg_circle = (
        '<circle cx="60" cy="60" r="48" fill="none" '
        'stroke="rgba(255,255,255,0.10)" stroke-width="10"/>'
    )
    return f"""
<div class="result-box" style="background:{result_style['background']};">
  <div class="result-icon">{result_style['icon']}</div>
  <h2>Final Assessment</h2>
  <h1>{final_label}</h1>
  <h3>{user_explanation}</h3>
  <div class="tg-indicators">
    <div class="tg-indicator-item">
      <div class="tg-ind-label">Model Confidence</div>
      <div class="tg-circle-wrap">
        <svg {_svg_attrs}>{_bg_circle}{ml_arc}</svg>
        <div class="tg-circle-inner">
          <span class="tg-circle-pct">{conf_display}</span>
        </div>
      </div>
      <div class="tg-circle-sub">{pred_label}</div>
      <div class="tg-circle-cat">{conf_cat} Confidence</div>
    </div>
    <div class="tg-indicator-item">
      <div class="tg-ind-label">Trusted Source Match</div>
      <div class="tg-circle-wrap">
        <svg {_svg_attrs}>{_bg_circle}{src_arc}</svg>
        <div class="tg-circle-inner">
          <span class="tg-circle-pct">{src_display}</span>
        </div>
      </div>
      <div class="tg-circle-sub">{src_cat}</div>
      <div class="tg-circle-cat">Trusted Malaysian Sources</div>
    </div>
  </div>
  <div class="tg-decision-basis">{basis}</div>
  <div class="tg-pct-note">
    These percentages measure writing patterns and source similarity, not truth or falsehood.
    See &ldquo;Why did I get this result?&rdquo; for the full explanation.
  </div>
</div>
"""


def render_submitted_news_expander(
    news_headline: str, news_url: str, news_content: str
) -> None:
    with st.expander("View Submitted News", expanded=False):
        st.caption(
            "This is the content used for the analysis shown below. "
            "The result will not change unless you submit a new article."
        )
        st.write("**Submitted headline:**")
        st.write(news_headline if news_headline.strip() else "Not provided")
        st.write("**Submitted URL:**")
        if news_url.strip():
            # URL passed validation — safe to render as a link.
            st.markdown(f"[{news_url}]({news_url})")
        else:
            st.write("Not provided")
        st.write("**Submitted news content:**")
        st.write(news_content)


def render_user_awareness_section(final_label: str, border_color: str) -> None:
    st.markdown(
        '<h3 style="color:#EAF6FF;margin:28px 0 4px;">'
        'User Awareness &amp; Safe Sharing Guidance</h3>'
        '<p style="color:#9DB4C8;font-size:.9rem;margin:0 0 14px;">'
        'Kesedaran Pengguna &amp; Panduan Perkongsian Selamat</p>',
        unsafe_allow_html=True,
    )
    malay_tab, english_tab = st.tabs(["Bahasa Melayu", "English"])
    with malay_tab:
        _render_awareness_tab("ms", final_label, border_color)
    with english_tab:
        _render_awareness_tab("en", final_label, border_color)


def _render_awareness_tab(lang_key: str, final_label: str, border_color: str) -> None:
    awareness_label = "Kesedaran Pengguna" if lang_key == "ms" else "Awareness Message"
    actions_label = "Tindakan Selamat" if lang_key == "ms" else "Safe Actions"

    awareness_text = html.escape(_AWARENESS_MESSAGES[final_label][lang_key])
    st.markdown(
        f'<div style="background:rgba(12,31,55,.82);border:1px solid {border_color}66;'
        f'border-radius:12px;padding:16px 20px;margin-bottom:12px;'
        f'color:#EAF6FF;line-height:1.75;font-size:.95rem;">'
        f'<div style="font-weight:700;font-size:.78rem;text-transform:uppercase;'
        f'letter-spacing:.07em;color:rgba(234,246,255,.60);margin-bottom:8px;">'
        f'{awareness_label}</div>'
        f'<div>{awareness_text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    items_html = "".join(
        f"<li style='margin-bottom:4px;'>{html.escape(item)}</li>"
        for item in _SAFE_ACTIONS[final_label][lang_key]
    )
    st.markdown(
        f'<div style="background:rgba(12,31,55,.65);border:1px solid {border_color}44;'
        f'border-radius:12px;padding:16px 20px;margin-bottom:4px;'
        f'color:#EAF6FF;line-height:1.75;font-size:.95rem;">'
        f'<div style="font-weight:700;font-size:.78rem;text-transform:uppercase;'
        f'letter-spacing:.07em;color:rgba(234,246,255,.60);margin-bottom:8px;">'
        f'{actions_label}</div>'
        f'<ul style="margin:0;padding-left:18px;">{items_html}</ul>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_why_expander(
    decision: dict,
    confidence: float,
    verification: dict,
    url_status: dict,
    probabilities: list,
    model,
) -> None:
    with st.expander("Why did I get this result?"):
        st.markdown("### Random Forest Prediction")
        class_proba = {int(cls): float(prob) for cls, prob in zip(model.classes_, probabilities)}
        real_prob = class_proba.get(0, 0.0) * 100
        fake_prob = class_proba.get(1, 0.0) * 100
        col_real, col_fake = st.columns(2)
        with col_real:
            st.markdown("**Real-news probability**")
            st.progress(min(int(real_prob), 100))
            st.caption(f"{real_prob:.2f}%")
        with col_fake:
            st.markdown("**Fake-news probability**")
            st.progress(min(int(fake_prob), 100))
            st.caption(f"{fake_prob:.2f}%")
        st.write(f"**Predicted writing pattern:** {decision['decision_path']['prediction_label']}")
        st.write(f"**Model confidence:** {confidence:.2f}%")
        st.write(
            f"**Confidence category:** {decision['confidence_category']} "
            f"(High >= 90% | Moderate >= 60% | Low < 60%)"
        )

        st.divider()

        st.markdown("### Malaysian Source Verification")
        headline_sim = verification["highest_headline_similarity"] * 100
        content_sim = verification["highest_content_similarity"] * 100
        final_sim = verification["highest_similarity"] * 100
        verification_category = decision["decision_path"]["verification_category"]

        st.write(f"**Headline used for verification:** {verification['headline_used']}")
        st.write(f"**Best article headline similarity:** {headline_sim:.2f}%")
        st.write(f"**Best article content similarity:** {content_sim:.2f}%")
        st.markdown("**Trusted Source Match calculation (best article):**")
        st.markdown(
            f"| Component | Weight | Value | Contribution |\n"
            f"|---|---|---|---|\n"
            f"| Headline similarity | 70% | {headline_sim:.2f}% | {headline_sim * 0.70:.2f}% |\n"
            f"| Content similarity | 30% | {content_sim:.2f}% | {content_sim * 0.30:.2f}% |\n"
            f"| **Final similarity** | | | **{final_sim:.2f}%** |"
        )
        st.caption(
            "The 70% headline and 30% content weighting applies to source-verification "
            "similarity only. All three values come from the single best-matching article."
        )
        st.write("**Final verification similarity:**")
        st.progress(min(int(final_sim), 100))
        st.caption(f"{final_sim:.2f}%")
        st.write(f"**Verification category:** {verification_category}")
        st.caption(
            f"Strong Match >= {STRONG_MATCH_THRESHOLD:.0%} | "
            f"Possible Match >= {POSSIBLE_MATCH_THRESHOLD:.0%} and below {STRONG_MATCH_THRESHOLD:.0%} | "
            f"No Match below {POSSIBLE_MATCH_THRESHOLD:.0%}"
        )

        if verification["status"] == "search_failed":
            st.error(f"External source verification failed: {verification['error']}")
        elif verification["status"] == "no_articles":
            st.warning("No related Malaysian article found.")
        elif verification["status"] == "strong_match":
            st.success("Trusted Malaysian source match found.")
        elif verification["status"] == "possible_match":
            st.warning(
                "Possible trusted Malaysian source match found. Similar content exists, "
                "but similarity is below the strong-match threshold."
            )
        else:
            st.warning("No trusted Malaysian source match found.")

        if not url_status["provided"]:
            st.info("No news URL was provided.")
            st.write("**Source domain detected:** Not provided")
            st.write("**Trusted domain status:** Not checked")
        elif url_status["trusted"]:
            st.success("Trusted Malaysian source domain detected.")
            st.write(f"**Source domain detected:** {url_status['domain']}")
            st.write("**Trusted domain status:** Trusted Malaysian domain")
        else:
            st.warning("Unverified or non-trusted source domain.")
            st.write(
                f"**Source domain detected:** "
                f"{url_status['domain'] or 'Unable to detect domain'}"
            )
            st.write("**Trusted domain status:** Unverified or non-trusted domain")
        st.caption(
            "Source verification and trusted-domain checks are supporting evidence only. "
            "They do not automatically prove that the news is real."
        )

        st.divider()

        st.markdown("### Applied Decision Rule")
        st.info(decision["rule_explanation"])

        st.divider()

        st.markdown("### Decision Path")
        dp = decision["decision_path"]
        st.markdown(
            f"- ML Prediction: **{dp['prediction_label']}**\n"
            f"- Model Confidence: **{dp['confidence']:.2f}%** ({dp['confidence_category']})\n"
            f"- Trusted Source Match: **{verification['highest_similarity']:.2f}%** ({dp['verification_category']})\n"
            f"- Applied Rule: *{dp['applied_rule']}*\n"
            f"- Final Assessment: **{dp['final_label']}**"
        )

        st.divider()

        st.markdown("### Important Notes")
        st.markdown(
            "- **Random Forest is the primary classifier.** "
            "Trusted-source verification provides supporting evidence only.\n"
            "- **No combined overall percentage exists.** "
            "Model confidence measures the model's certainty about writing patterns. "
            "Trusted Source Match measures how closely a trusted article matches the submitted text. "
            "They measure different things and are never mathematically combined.\n"
            "- **The final assessment uses decision rules**, not a blended score. "
            "Each rule is listed under the Applied Decision Rule section above.\n"
            "- **Similarity does not prove an article is true.** "
            "A similar article may exist but cover a different context or time period.\n"
            "- **A trusted domain does not automatically mean the submitted claim is true.** "
            "Trusted outlets can be misquoted or taken out of context."
        )


def render_articles_expander(matched_articles: list) -> None:
    with st.expander("Related Trusted Articles"):
        if matched_articles:
            for article in matched_articles[:6]:
                title = article.get("title") or "Untitled article"
                source = article.get("source", {}).get("name") or article["domain"]
                st.markdown(f"**{title}**")
                st.caption(
                    f"{source} | {article['domain']} | "
                    f"Headline: {article['headline_similarity']:.0%} | "
                    f"Content: {article['content_similarity']:.0%} | "
                    f"Final: {article['similarity']:.0%}"
                )
                if article.get("description"):
                    st.write(article["description"])
                if article.get("url"):
                    st.markdown(f"[Open source article]({article['url']})")
                st.markdown("---")
        else:
            st.write("No trusted Malaysian articles met the possible-match threshold.")


def render_advanced_expander(
    language_name: str,
    language_code: str,
    news_content: str,
    translated_text: str | None,
    cleaned_text: str,
    verification: dict,
) -> None:
    from config import TRUSTED_DOMAINS, STRONG_MATCH_THRESHOLD, POSSIBLE_MATCH_THRESHOLD
    with st.expander("Advanced Technical Details"):
        lang_tab, tech_tab = st.tabs(["Language & Translation", "Technical Information"])

        with lang_tab:
            st.write(f"**Detected language:** {language_name}")
            st.write("**Original text:**")
            st.write(news_content)
            st.write("**Translated English text:**")
            if translated_text:
                st.write(translated_text)
            elif language_code == "ms":
                st.write("Translation was unavailable. The original text was used.")
            else:
                st.write("Translation was not required.")

        with tech_tab:
            st.write(
                f"**Search keywords:** "
                f"{', '.join(verification['keywords']) if verification['keywords'] else 'None found'}"
            )
            st.write("**Queries and domains searched:**")
            for query, domains in zip(
                verification["queries_used"], verification["domains_searched"]
            ):
                st.code(f"Query: {query}\nDomains: {domains}")
            st.write(
                f"**Malaysian results before similarity filtering:** "
                f"{verification['trusted_count']} (Google News RSS + cached feeds + DuckDuckGo)"
            )
            st.write(
                f"**Best article headline similarity:** "
                f"{verification['highest_headline_similarity']:.2%}"
            )
            st.write(
                f"**Best article content similarity:** "
                f"{verification['highest_content_similarity']:.2%}"
            )
            st.write(
                f"**Final similarity score (best article):** {verification['highest_similarity']:.2%}"
            )
            if verification["source_hint"]:
                st.write(
                    f"**Trusted source hint detected:** {verification['source_hint']} "
                    "(included as a keyword in the search query)"
                )
            if verification["url_domain_hint"]:
                st.write(
                    f"**URL domain hint:** {verification['url_domain_hint']} -- "
                    "included as a keyword in the search query; does not change the final assessment directly."
                )
            st.write(f"**Processed English model text:** {cleaned_text}")
            st.write(f"**Trusted domains searched:** {', '.join(TRUSTED_DOMAINS)}")
            st.write(
                f"**Match thresholds:** Strong >= {STRONG_MATCH_THRESHOLD:.0%}; "
                f"Possible >= {POSSIBLE_MATCH_THRESHOLD:.0%}"
            )
            st.write("**Similarity weighting:** Headline 70%; Content 30%")
