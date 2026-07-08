"""Συναρτήσεις λήψης HTML περιεχομένου (απευθείας URL ή μέσω Wikipedia API)."""
import re
import urllib.request
import urllib.parse


def fetch_html(url: str) -> str:
    """Κατεβάζει το ωμό HTML μιας σελίδας από το URL της."""
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8")


def fetch_wiki_api(page_title: str, lang: str = "el") -> str:
    """Χρησιμοποιεί το Wikipedia API για να πάρει το καθαρό HTML της σελίδας."""
    api_url = (
        f"https://{lang}.wikipedia.org/w/api.php"
        f"?action=parse&page={urllib.parse.quote(page_title)}"
        f"&prop=text&format=json&utf8=1"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = response.read().decode("utf-8")

    # Εξαγωγή του HTML από το JSON με regex
    m = re.search(r'"text"\s*:\s*\{\s*"\*"\s*:\s*"(.*?)"\s*\}', data, re.DOTALL)
    if not m:
        return ""

    # Αποκωδικοποίηση unicode escapes (π.χ. \u003c → <)
    html_escaped = m.group(1)
    html_clean = (
        html_escaped.encode("utf-8")
        .decode("unicode_escape")
        .encode("latin-1")
        .decode("utf-8")
    )
    return html_clean


def parse_url_info(url: str) -> tuple[str, str]:
    """Εξάγει τη γλώσσα και τον τίτλο σελίδας από ένα Wikipedia URL."""
    lang_m = re.search(r"https?://([a-z]{2,3})\.wikipedia\.org", url, re.IGNORECASE)
    title_m = re.search(r"/wiki/([^?#]+)", url)
    lang = lang_m.group(1) if lang_m else "el"
    page_title = urllib.parse.unquote(title_m.group(1)) if title_m else ""
    return lang, page_title
