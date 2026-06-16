from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TRUSTED_DOMAINS = (
    "bernama.com",
    "rtm.gov.my",
    "berita.rtm.gov.my",
    "sebenarnya.my",
    "jomcheck.org",
    "thestar.com.my",
    "nst.com.my",
    "malaymail.com",
    "freemalaysiatoday.com",
    "malaysiakini.com",
    "themalaysianreserve.com",
    "theedgemalaysia.com",
    "thevibes.com",
    "bharian.com.my",
    "hmetro.com.my",
    "sinarharian.com.my",
    "utusan.com.my",
    "kosmo.com.my",
    "astroawani.com",
    "malaysia.news.yahoo.com",
    "therakyatpost.com",
    "says.com",
    "vulcanpost.com",
    "lowyat.net",
)

STRONG_MATCH_THRESHOLD = 0.15
POSSIBLE_MATCH_THRESHOLD = 0.10

WEAK_SEARCH_WORDS = {
    "said", "today", "june", "datuk", "seri", "bernama", "kuala", "lumpur",
}

SOURCE_DOMAIN_HINTS = {
    "bernama": "bernama.com",
    "berita rtm": "berita.rtm.gov.my",
    "rtm": "rtm.gov.my",
    "sebenarnya": "sebenarnya.my",
    "jomcheck": "jomcheck.org",
    "the star": "thestar.com.my",
    "new straits times": "nst.com.my",
    "malay mail": "malaymail.com",
    "free malaysia today": "freemalaysiatoday.com",
    "malaysiakini": "malaysiakini.com",
    "the malaysian reserve": "themalaysianreserve.com",
    "the edge malaysia": "theedgemalaysia.com",
    "the vibes": "thevibes.com",
    "berita harian": "bharian.com.my",
    "harian metro": "hmetro.com.my",
    "sinar harian": "sinarharian.com.my",
    "utusan malaysia": "utusan.com.my",
    "kosmo": "kosmo.com.my",
    "astro awani": "astroawani.com",
    "yahoo malaysia": "malaysia.news.yahoo.com",
    "the rakyat post": "therakyatpost.com",
    "says malaysia": "says.com",
    "vulcan post": "vulcanpost.com",
    "lowyat": "lowyat.net",
}

MALAY_STOPWORDS = {
    "ada", "adalah", "akan", "atau", "bagi", "bahawa", "dan", "dari", "daripada",
    "dengan", "di", "ini", "itu", "juga", "ke", "kepada", "kerana", "oleh", "pada",
    "sebagai", "telah", "untuk", "yang",
}

_GNEWS = "https://news.google.com/rss/search?q=site:{domain}&hl=en-MY&gl=MY&ceid=MY:en"

TRUSTED_RSS_FEEDS = [
    ("bernama.com",           _GNEWS.format(domain="bernama.com")),
    ("thestar.com.my",        _GNEWS.format(domain="thestar.com.my")),
    ("nst.com.my",            _GNEWS.format(domain="nst.com.my")),
    ("astroawani.com",        _GNEWS.format(domain="astroawani.com")),
    ("bharian.com.my",        _GNEWS.format(domain="bharian.com.my")),
    ("malaymail.com",         _GNEWS.format(domain="malaymail.com")),
    ("malaysiakini.com",      _GNEWS.format(domain="malaysiakini.com")),
    ("hmetro.com.my",         _GNEWS.format(domain="hmetro.com.my")),
    ("sinarharian.com.my",    _GNEWS.format(domain="sinarharian.com.my")),
    ("utusan.com.my",         _GNEWS.format(domain="utusan.com.my")),
    ("theedgemalaysia.com",   _GNEWS.format(domain="theedgemalaysia.com")),
    ("freemalaysiatoday.com", "https://www.freemalaysiatoday.com/feed/"),
    ("therakyatpost.com",     "https://www.therakyatpost.com/feed"),
    ("thevibes.com",          "https://www.thevibes.com/rss"),
    ("vulcanpost.com",        "https://vulcanpost.com/feed/"),
    ("lowyat.net",            "https://www.lowyat.net/feed"),
]

RSS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

CONTENT_MAX_LENGTH = 5000
HEADLINE_MAX_LENGTH = 300
