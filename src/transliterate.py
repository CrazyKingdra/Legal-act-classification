"""Serbian Cyrillic -> Latin transliteration (one-to-one standard mapping)."""
import re

_MAP = {
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Ђ": "Đ", "Е": "E", "Ж": "Ž",
    "З": "Z", "И": "I", "Ј": "J", "К": "K", "Л": "L", "Љ": "Lj", "М": "M", "Н": "N",
    "Њ": "Nj", "О": "O", "П": "P", "Р": "R", "С": "S", "Т": "T", "Ћ": "Ć", "У": "U",
    "Ф": "F", "Х": "H", "Ц": "C", "Ч": "Č", "Џ": "Dž", "Ш": "Š",
}
_MAP.update({k.lower(): v.lower() for k, v in _MAP.items()})
_CYR = re.compile("[\u0400-\u04FF]")


def cyrillic_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if _CYR.match(c)) / len(letters)


def detect_script(text: str) -> str:
    return "cyrillic" if cyrillic_ratio(text) > 0.5 else "latin"


def to_latin(text: str) -> str:
    out = []
    for i, ch in enumerate(text):
        lat = _MAP.get(ch)
        if lat is None:
            out.append(ch)
            continue
        # Digraphs (Lj, Nj, Dž) become all-caps inside all-caps words: ЉУБАВ -> LJUBAV
        if len(lat) == 2 and ch.isupper():
            nxt = text[i + 1] if i + 1 < len(text) else ""
            prv = text[i - 1] if i > 0 else ""
            if (nxt.isalpha() and nxt.isupper()) or (not nxt.isalpha() and prv.isalpha() and prv.isupper()):
                lat = lat.upper()
        out.append(lat)
    return "".join(out)


if __name__ == "__main__":
    import sys
    print(to_latin(sys.stdin.read()))
