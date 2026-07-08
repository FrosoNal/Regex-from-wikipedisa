"""Συναρτήσεις εξαγωγής πληροφοριών πόλης από HTML περιεχόμενο Wikipedia."""
import re

from text_utils import strip_tags, clean_number, clean_text


def extract_title(html: str) -> str | None:
    """1. Όνομα πόλης – από τον τίτλο της σελίδας."""
    m = re.search(r"<title>(.*?)\s*[-–]\s*Βικιπαίδεια</title>", html, re.IGNORECASE)
    if m:
        return strip_tags(m.group(1))
    m = re.search(r"<title>(.*?)\s*[-–]\s*Wikipedia</title>", html, re.IGNORECASE)
    if m:
        return strip_tags(m.group(1))
    return None


def extract_population(html: str) -> str | None:
    """2. Πληθυσμός."""
    patterns = [
        r"Πληθυσμός[^\n]{0,400}?(\b\d[\d\s,.]{2,}\d\b)",
        r'population_total\s*=\s*([\d,. ]+)',
        r'(?:Population|Πληθυσμός)[^<]{0,10}<[^>]+>\s*([\d,. ]+)',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        if m:
            val = clean_number(m.group(1))
            if re.search(r"\d{3,}", val):
                return val
    return None


def extract_area(html: str) -> str | None:
    """3. Έκταση (εμβαδό)."""
    patterns = [
        r"Έκταση[^\n]{0,400}?(\b\d[\d\s,.]{2,}\d\b)",
        r'area_total_km2\s*=\s*([\d,. ]+)',
        r'(?:Area|Έκταση)[^<]{0,10}<[^>]+>\s*([\d,. ]+)',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        if m:
            val = clean_number(m.group(1))
            if re.search(r"\d{2,}", val):
                return val
    return None


def extract_country(html: str) -> str | None:
    """4. Χώρα / Περιφέρεια."""
    patterns = [
        r"Χώρα\s*(?:</[^>]+>)*\s*(?:<[^>]+>)*\s*([^\n<]{2,60})",
        r'subdivision_name\s*=\s*\[\[([^\]]+)\]\]',
        r"Country[^<]{0,10}<[^>]+>\s*([^\n<]{2,60})",
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        if m:
            raw = strip_tags(m.group(1))
            raw = re.sub(r"\s+", " ", raw).strip()
            if 2 < len(raw) < 60:
                return raw
    return None


def extract_coordinates(html: str) -> str | None:
    """5. Γεωγραφικές συντεταγμένες."""
    patterns = [
        (r'class="geo"[^>]*>\s*([\d.]+)\s*;\s*([\d.]+)\s*<',            True),
        (r'data-lat="([\d.]+)"[^>]*data-lon="([\d.]+)"',                True),
        (r'data-lon="([\d.]+)"[^>]*data-lat="([\d.]+)"',                True),
        (r'geohack[^"]*?params=([\d.]+)[_/]([\d.]+)',                    True),
        (r'latitude\s*=\s*([\d.]+)[^\d]{1,10}longitude\s*=\s*([\d.]+)', True),
        (r'class="geo-dec"[^>]*>\s*([^<]{4,40})<',                      False),
    ]
    for pat, two_groups in patterns:
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        if m:
            if two_groups:
                return f"{m.group(1).strip()}°N, {m.group(2).strip()}°E"
            else:
                return strip_tags(m.group(1)).strip()
    return None


def extract_altitude(html: str) -> str | None:
    """6. Υψόμετρο."""
    patterns = [
        r"Υψόμετρο[^<]*(?:<[^>]+>)*\s*</(?:th|td)>.*?<td[^>]*>(.*?)</td>",
        r"Υψόμετρο[^\n]{0,400}?(\b\d[\d\s,.]{0,10}\d\b)",
        r'elevation_m\s*=\s*([\d,. ]+)',
        r'(?:Elevation|Υψόμετρο)[^<]{0,10}<[^>]+>\s*([\d,. ]+)',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        if m:
            raw = strip_tags(m.group(1))
            raw = re.sub(r"[^\d.,\s]", "", raw).strip()
            if re.search(r"\d+", raw):
                return raw
    return None


def extract_timezone(html: str) -> str | None:
    """7. Ζώνη ώρας."""
    patterns = [
        r"Ζώνη\s*ώρας[^<]*(?:<[^>]+>)*\s*([^<\n]{3,40})",
        r"Ώρα[^<]{0,30}?UTC\s*([+−\-][\d:]+)",
        r'timezone(?:1)?\s*=\s*([^\n|]{3,40})',
        r'utc_offset(?:1)?\s*=\s*([+\-−][\d:]+)',
        r"UTC\s*([+−\-]\d{1,2}(?::\d{2})?)",
        r'class="timezone"[^>]*>\s*([^<]{3,40})',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        if m:
            raw = strip_tags(m.group(1)).strip()
            raw = re.sub(r"\s+", " ", raw)
            if 2 < len(raw) < 50:
                return raw
    return None


def extract_temperature(html: str) -> dict | None:
    """8. Στοιχεία θερμοκρασίας από πίνακα κλίματος (μέση, ελάχιστη, μέγιστη)."""
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL | re.IGNORECASE)

    result = {}
    f_val = None

    for row in rows:
        header = strip_tags(
            " ".join(re.findall(r"<th[^>]*>(.*?)</th>", row, re.DOTALL))
        ).lower()

        text = clean_text(strip_tags(row))

        # βρίσκουμε όλα τα pairs "x (y)"
        pairs = re.findall(r"(-?\d+(?:[.,]\d+)?)\s*\((\-?\d+(?:[.,]\d+)?)\)", text)

        # fallback (αν δεν υπάρχουν παρενθέσεις)
        singles = re.findall(r"(-?\d+(?:[.,]\d+)?)", text)

        c_val = None

        if pairs:
            # Wikipedia standard: first = °C, second = °F
            c_val = float(pairs[-1][0].replace(",", "."))
            f_val = float(pairs[-1][1].replace(",", "."))
        elif singles:
            c_val = float(singles[-1].replace(",", "."))

        # assign values σωστά
        if "μέση μηνιαία" in header:
            if c_val is not None:
                result["mean"] = c_val

        elif "χαμηλότερη ελάχιστη" in header:
            if c_val is not None:
                result["lowest_min"] = c_val

        elif "υψηλότερη μέγιστη" in header:
            if c_val is not None:
                result["highest_max"] = c_val

    # σωστό unit detection
    if f_val is not None:
        result["unit"] = "Celsius (Fahrenheit also present)"
        result["fahrenheit_detected"] = True
    else:
        result["unit"] = "Celsius"
        result["fahrenheit_detected"] = False

    return result if result else None
