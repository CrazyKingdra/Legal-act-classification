"""Heuristic ekavian / ijekavian detector.

Counts word stems that differ between the two reflexes of jat
(e.g. vrijeme/vreme, mjesto/mesto, rješenje/rešenje). Works on Latin text,
so transliterate first.
"""
import re

# (ijekavian stem, ekavian stem) pairs that are frequent in legal text
PAIRS = [
    ("vrijem", "vrem"), ("mjest", "mest"), ("mjer", "mer"), ("rješ", "reš"),
    ("primjen", "primen"), ("promjen", "promen"), ("izmjen", "izmen"),
    ("vrijed", "vred"), ("cjelin", "celin"), ("prijedlog", "predlog"),
    ("obavješt", "obavešt"), ("djelatn", "delatn"), ("djelokrug", "delokrug"),
    ("sjedišt", "sedišt"), ("mjesec", "mesec"), ("bilježn", "beležn"),
    ("svjedo", "svedo"), ("procjen", "procen"), ("ocjen", "ocen"),
    ("zahtjev", "zahtev"), ("savjet", "savet"), ("dijelov", "delov"),
    ("nadzir", "nadzir"),
]
PAIRS = [(i, e) for i, e in PAIRS if i != e]
_WORD = re.compile(r"\w+", re.UNICODE)


def detect_dialect(text: str, min_hits: int = 5) -> str:
    ije = eka = 0
    for w in _WORD.findall(text.lower()):
        for i_stem, e_stem in PAIRS:
            if w.startswith(i_stem):
                ije += 1
                break
            if w.startswith(e_stem):
                eka += 1
                break
    if ije + eka < min_hits:
        return "unknown"
    return "ijekavian" if ije > eka else "ekavian"
