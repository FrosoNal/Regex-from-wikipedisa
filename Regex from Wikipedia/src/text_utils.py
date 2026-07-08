"""Βοηθητικές συναρτήσεις καθαρισμού κειμένου/αριθμών."""
import re


def strip_tags(text: str) -> str:
    """Αφαιρεί όλα τα HTML tags από ένα string."""
    return re.sub(r"<[^>]+>", "", text).strip()


def clean_number(raw: str) -> str:
    """Καθαρίζει ένα string ώστε να μείνουν μόνο ψηφία, τελείες και κόμματα."""
    raw = strip_tags(raw)
    raw = re.sub(r"\s+", "", raw)
    raw = re.sub(r"[^\d.,]", "", raw)
    return raw


def clean_text(text: str) -> str:
    """Αντικαθιστά το ειδικό σύμβολο μείον (−) με το κανονικό (-)."""
    return text.replace("−", "-")
