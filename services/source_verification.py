import re
import time
from urllib.parse import urlparse

import feedparser
import requests
import streamlit as st
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    TRUSTED_DOMAINS,
    TRUSTED_RSS_FEEDS,
    RSS_HEADERS,
    STRONG_MATCH_THRESHOLD,
    POSSIBLE_MATCH_THRESHOLD,
)
from utils.text_processing import extract_keywords, extract_first_sentence, detect_source_hint


def get_domain(url: str) -> str:
    normalized = (url or "").strip()
    if normalized and "://" not in normalized:
        normalized = f"//{normalized}"
    domain = (urlparse(normalized).hostname or "").lower()
    return domain.removeprefix("www.")


def is_trusted_malaysian_domain(url: str) -> bool:
    domain = get_domain(url)
    return any(domain == t or domain.endswith(f".{t}") for t in TRUSTED_DOMAINS)


def assess_news_url(url: str) -> dict:
    url = url.strip()
    if not url:
        return {"provided": False, "domain": "", "trusted": False}
    return {
        "provided": True,
        "domain": get_domain(url),
        "trusted": is_trusted_malaysian_domain(url),
    }


def calculate_similarity(user_text: str, article_text: str) -> float:
    if not user_text.strip() or not article_text.strip():
        return 0.0
    sim_tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    first_sentence = extract_first_sentence(user_text)
    vectors = sim_tfidf.fit_transform([user_text, first_sentence, article_text])
    full_score = cosine_similarity(vectors[0:1], vectors[2:3])[0][0]
    sentence_score = cosine_similarity(vectors[1:2], vectors[2:3])[0][0]
    return float(max(full_score, sentence_score))


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_rss_articles() -> list:
    articles = []
    for domain, feed_url in TRUSTED_RSS_FEEDS:
        try:
            response = requests.get(feed_url, headers=RSS_HEADERS, timeout=10)
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:30]:
                url = entry.get("link", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                summary = re.sub(r"<[^>]+>", " ", summary).strip()
                articles.append({
                    "title": entry.get("title", ""),
                    "description": summary,
                    "content": summary,
                    "url": url,
                    "source": {"name": domain},
                })
        except Exception:
            continue
    return articles


def search_ddg_trusted(query: str) -> list:
    site_filter = " OR ".join(f"site:{d}" for d in TRUSTED_DOMAINS)
    restricted_query = f"{query} ({site_filter})"
    for attempt in range(2):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(restricted_query, max_results=20))
            articles = []
            for r in results:
                url = r.get("href", "")
                if is_trusted_malaysian_domain(url):
                    articles.append({
                        "title": r.get("title", ""),
                        "description": r.get("body", ""),
                        "content": r.get("body", ""),
                        "url": url,
                        "source": {"name": get_domain(url)},
                    })
            return articles
        except DuckDuckGoSearchException:
            if attempt == 0:
                time.sleep(3)
            continue
        except Exception:
            break
    return []


@st.cache_data(ttl=900, show_spinner=False)
def search_gnews(query: str) -> list:
    base_url = "https://news.google.com/rss/search"
    params = {"q": query, "hl": "en-MY", "gl": "MY", "ceid": "MY:en"}
    try:
        response = requests.get(base_url, params=params, headers=RSS_HEADERS, timeout=10)
        feed = feedparser.parse(response.content)
        articles = []
        for entry in feed.entries[:20]:
            gnews_url = entry.get("link", "")
            source_href = (entry.get("source") or {}).get("href", "")
            source_name = (entry.get("source") or {}).get("title", "")
            real_domain = get_domain(source_href) if source_href else ""
            summary = re.sub(r"<[^>]+>", " ", entry.get("summary", "")).strip()
            articles.append({
                "title": entry.get("title", ""),
                "description": summary,
                "content": summary,
                "url": gnews_url,
                "_real_domain": real_domain,
                "source": {"name": source_name or real_domain},
            })
        return articles
    except Exception:
        return []


@st.cache_data(ttl=900, show_spinner=False)
def search_trusted_news(query: str) -> list:
    articles_by_url = {}

    for article in search_gnews(query):
        url = article.get("url", "")
        real_domain = article.get("_real_domain", "")
        is_trusted = any(
            real_domain == d or real_domain.endswith(f".{d}") for d in TRUSTED_DOMAINS
        )
        if url and is_trusted and url not in articles_by_url:
            articles_by_url[url] = article

    keywords = set(re.findall(r"[a-zA-Z]{3,}", query.lower()))
    for article in fetch_rss_articles():
        combined = f"{article['title']} {article['description']}".lower()
        if any(kw in combined for kw in keywords):
            url = article["url"]
            if url and url not in articles_by_url:
                articles_by_url[url] = article

    if len(articles_by_url) < 5:
        for article in search_ddg_trusted(query):
            url = article.get("url", "")
            if url and url not in articles_by_url:
                articles_by_url[url] = article

    return list(articles_by_url.values())


def verify_with_malaysian_sources(
    headline: str, content: str, trusted_url_domain: str | None = None
) -> dict:
    headline = headline.strip()
    content = content.strip()
    content_keywords = extract_keywords(content)
    headline_used = headline or extract_first_sentence(content)
    source_hint = trusted_url_domain or detect_source_hint(f"{headline} {content}")

    hint_prefix = f"site:{source_hint} " if source_hint else ""

    if headline:
        queries = [
            f"{hint_prefix}{headline}",
            " ".join([headline, *content_keywords[:5]]),
            " OR ".join(content_keywords[:5]),
        ]
    else:
        queries = [
            f"{hint_prefix}{headline_used}",
            " OR ".join(content_keywords[:5]),
            " OR ".join(content_keywords[:3]),
        ]

    result = {
        "keywords": content_keywords,
        "headline_used": headline_used,
        "status": "search_failed",
        "error": None,
        "search_result_count": 0,
        "trusted_count": 0,
        "matched_articles": [],
        "queries_used": [],
        "domains_searched": [],
        "source_hint": source_hint,
        "url_domain_hint": trusted_url_domain,
        "highest_similarity": 0.0,
        "highest_headline_similarity": 0.0,
        "highest_content_similarity": 0.0,
    }
    if not content_keywords and not headline_used:
        result["error"] = "No useful keywords could be extracted for the trusted source search."
        return result

    articles_by_url = {}
    search_errors = []
    for query in queries:
        if not query or query in result["queries_used"]:
            continue
        result["queries_used"].append(query)
        result["domains_searched"].append(",".join(TRUSTED_DOMAINS))
        try:
            for article in search_trusted_news(query):
                url = article.get("url")
                real_domain = article.get("_real_domain", "")
                trusted = (
                    any(real_domain == d or real_domain.endswith(f".{d}") for d in TRUSTED_DOMAINS)
                    if real_domain else is_trusted_malaysian_domain(url)
                )
                if url and trusted:
                    articles_by_url[url] = article
        except requests.RequestException as error:
            search_errors.append(str(error))

    trusted_articles = list(articles_by_url.values())
    result["search_result_count"] = len(trusted_articles)
    result["trusted_count"] = len(trusted_articles)
    if not trusted_articles:
        if search_errors and len(search_errors) == len(result["queries_used"]):
            result["error"] = search_errors[0]
            return result
        result["status"] = "no_articles"
        return result

    scored_articles = []
    for article in trusted_articles:
        article_title = article.get("title") or ""
        article_content = " ".join([
            article.get("description") or "",
            article.get("content") or "",
        ]).strip()
        headline_similarity = calculate_similarity(headline_used, article_title)
        content_similarity = calculate_similarity(content, article_content)
        final_similarity = (headline_similarity * 0.7) + (content_similarity * 0.3)
        scored_articles.append({
            **article,
            "domain": article.get("_real_domain") or get_domain(article.get("url")),
            "headline_similarity": headline_similarity,
            "content_similarity": content_similarity,
            "similarity": final_similarity,
        })

    # Use values from the single best article so all three scores are consistent.
    best = max(scored_articles, key=lambda a: a["similarity"])
    result["highest_similarity"] = best["similarity"]
    result["highest_headline_similarity"] = best["headline_similarity"]
    result["highest_content_similarity"] = best["content_similarity"]

    result["matched_articles"] = sorted(
        [a for a in scored_articles if a["similarity"] >= POSSIBLE_MATCH_THRESHOLD],
        key=lambda a: a["similarity"],
        reverse=True,
    )

    if result["highest_similarity"] >= STRONG_MATCH_THRESHOLD:
        result["status"] = "strong_match"
    elif result["highest_similarity"] >= POSSIBLE_MATCH_THRESHOLD:
        result["status"] = "possible_match"
    else:
        result["status"] = "no_match"

    return result
