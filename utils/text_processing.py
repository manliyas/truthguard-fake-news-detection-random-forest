import re
from collections import Counter

from langdetect import DetectorFactory, LangDetectException, detect
from deep_translator import GoogleTranslator
import streamlit as st

from config import MALAY_STOPWORDS, WEAK_SEARCH_WORDS

DetectorFactory.seed = 0

_lemmatizer = None
_english_stopwords: set = set()


def init(lemmatizer, english_stopwords: set) -> None:
    global _lemmatizer, _english_stopwords
    _lemmatizer = lemmatizer
    _english_stopwords = english_stopwords


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    words = text.split()
    words = [_lemmatizer.lemmatize(word) for word in words if word not in _english_stopwords]
    return " ".join(words)


def detect_input_language(text: str) -> tuple[str, str]:
    try:
        language_code = detect(text)
    except LangDetectException:
        return "unknown", "Unknown"
    if language_code in {"ms", "id"}:
        return "ms", "Malay"
    if language_code == "en":
        return "en", "English"
    return language_code, f"Other ({language_code})"


@st.cache_data(ttl=3600, show_spinner=False)
def translate_malay_to_english(text: str) -> str | None:
    try:
        return GoogleTranslator(source="ms", target="en").translate(text[:4500])
    except Exception:
        return None


def extract_keywords(text: str, limit: int = 10) -> list[str]:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    ignored = _english_stopwords | MALAY_STOPWORDS | WEAK_SEARCH_WORDS
    useful_words = [word for word in words if word not in ignored]
    first_position = {word: useful_words.index(word) for word in set(useful_words)}
    counts = Counter(useful_words)
    ranked_words = sorted(counts, key=lambda word: (-counts[word], first_position[word]))
    return ranked_words[:limit]


def extract_first_sentence(text: str, max_words: int = 18) -> str:
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), text.strip())
    first_sentence = re.split(r"(?<=[.!?])\s+", first_line, maxsplit=1)[0]
    words = re.findall(r"[a-zA-Z0-9'-]+", first_sentence)
    return " ".join(words[:max_words])


def detect_source_hint(text: str) -> str | None:
    from config import SOURCE_DOMAIN_HINTS
    lowered = text.lower()
    for source_name, domain in SOURCE_DOMAIN_HINTS.items():
        if source_name in lowered:
            return domain
    return None
