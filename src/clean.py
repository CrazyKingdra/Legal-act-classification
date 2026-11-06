"""Text cleaning shared by all sources."""
import re
import unicodedata

from .dialect import detect_dialect
from .transliterate import detect_script, to_latin

_PAGE_NUM = re.compile(r"^\s*(strana|stranica|str\.|page)?\s*\d+\s*(/\s*\d+)?\s*$", re.I)
_GAZETTE_HEADER = re.compile(
    r"^\s*(narodne novine|službeni glasnik|službeni list|службени гласник|службени лист).{0,60}$", re.I)
# Serbian PIS (pravno-informacioni-sistem.rs): first line of every text link
_DOWNLOADED_FROM = re.compile(
    r"^\s*(преузето\s+са|preuzeto\s+sa)\s+https?://\S+\s*$", re.I)
# Bosnian sluzbenilist.ba: banner the portal adds above some acts (not part of the act)
_PORTAL_NOTICE = re.compile(r"ovaj\s+akt\s+nije\s+une[sš]en\s+na\s+\w+\s+jeziku\.?", re.I)


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u00ad", "")              # soft hyphens
    text = _PORTAL_NOTICE.sub("", text)            # portal banner (can share a line with text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)   # words split across lines in PDFs
    lines = []
    for line in text.splitlines():
        if _PAGE_NUM.match(line) or _GAZETTE_HEADER.match(line) or _DOWNLOADED_FROM.match(line):
            continue
        lines.append(re.sub(r"[ \t]+", " ", line).strip())
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def guess_title(text: str) -> str:
    """First line that looks like an act title (ZAKON / UREDBA / PRAVILNIK / ODLUKA ...)."""
    for line in text.splitlines()[:40]:
        if re.match(r"^(zakon|uredb|pravilnik|odluk|naredb|uputstv|naputak|rješenj|rešenj)", line, re.I) \
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