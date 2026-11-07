"""Text cleaning shared by all sources."""
import re
import unicodedata

from .dialect import detect_dialect
from .transliterate import detect_script, to_latin

# Set to False if you want to keep the "Službeni glasnik ... broj X od <date>" citation lines
STRIP_GAZETTE_CITATION = True

_PAGE_NUM = re.compile(r"^\s*(strana|stranica|str\.|page)?\s*\d+\s*(/\s*\d+)?\s*$", re.I)
_GAZETTE_HEADER = re.compile(
    r"^\s*(narodne novine|službeni glasnik|službeni list|службени гласник|службени лист).{0,60}$", re.I)

# Citation line such as: "Službeni glasnik RS", br. 10 od 9. februara 2023, 56 od 25. juna 2026.
_GAZETTE_CITATION = re.compile(
    r"^\s*[\"„“”']*\s*(službeni\s+(glasnik|list)|службени\s+(гласник|лист))"
    r".{0,400}?(broj|br\.|број|бр\.).{0,400}?\d{4}\.?\s*$", re.I)

# Serbian PIS (pravno-informacioni-sistem.rs)
_DOWNLOADED_FROM = re.compile(
    r"^\s*(преузето\s+са|preuzeto\s+sa)\s+https?://\S+\s*$", re.I)
_REDAKCIJSKI = re.compile(
    r"^\s*(редакцијски|redakcijski)\s+(пречишћен|prečišćen)\s+(текст|tekst)\s*$", re.I)

# Bosnian sluzbenilist.ba: banner above some acts
_PORTAL_NOTICE = re.compile(r"ovaj\s+akt\s+nije\s+une[sš]en\s+na\s+\w+\s+jeziku\.?", re.I)
# Bosnian sluzbenilist.ba: subscriber footer (everything from here to the end is portal text)
_BS_FOOTER = re.compile(
    r"(?:\n[ \t]*r\.[ \t]*)?\s*Pretplatnici\s+imaju\s+dodatne\s+pogodnosti.*\Z",
    re.I | re.S)
_BS_COPYRIGHT = re.compile(
    r"^\s*\d{4}\s*©\s*JP\s+NIO.*$", re.I | re.M)

# Frequent OCR slip in Serbian PDFs: Latin "Ha osnovu" instead of "На основу"
_OCR_FIXES = [
    (re.compile(r"^Ha osnovu\b", re.M), "Na osnovu"),
    (re.compile(r"\bСлужбени гласник PC\b"), "Службени гласник RS"),
    (re.compile(r"\bSlužbeni glasnik PC\b"), "Službeni glasnik RS"),
]


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u00ad", "")              # soft hyphens
    text = _PORTAL_NOTICE.sub("", text)            # portal banner (can share a line with text)
    text = _BS_FOOTER.sub("", text)                # sluzbenilist.ba footer
    text = _BS_COPYRIGHT.sub("", text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)   # words split across lines in PDFs
    for pat, repl in _OCR_FIXES:
        text = pat.sub(repl, text)
    lines = []
    for line in text.splitlines():
        if (_PAGE_NUM.match(line) or _GAZETTE_HEADER.match(line)
                or _DOWNLOADED_FROM.match(line) or _REDAKCIJSKI.match(line)):
            continue
        if STRIP_GAZETTE_CITATION and _GAZETTE_CITATION.match(line):
            continue
        lines.append(re.sub(r"[ \t]+", " ", line).strip())
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def guess_title(text: str) -> str:
    """First line that looks like an act title (ZAKON / UREDBA / PRAVILNIK / ODLUKA ...)."""
    for line in text.splitlines()[:40]:
        if re.match(r"^(zakon|uredb|pravilnik|odluk|naredb|uputstv|naputak|rješenj|rešenj"
                    r"|zaključ|rezolucij|preporuk|instrukcij|deklaracij)", line, re.I) \
                and len(line) < 300:
            return line
    return ""


def clean_record(rec: dict) -> dict:
    orig = normalise(rec["text"])
    script = detect_script(orig)
    latin = to_latin(orig) if script == "cyrillic" else orig
    title = rec.get("title") or guess_title(latin)
    rec.update({
        "text_orig": orig,
        "text": latin,
        "title": to_latin(title),
        "script": script,
        "dialect": detect_dialect(latin),
    })
    return rec
