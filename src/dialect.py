"""Heuristic ekavian / ijekavian detector.

Counts words that differ between the two reflexes of jat
(vrijeme/vreme, sjednica/sednica, gdje/gde ...). Works on Latin text,
so transliterate first.

Returns "ijekavian", "ekavian" or "unknown". "unknown" means: too few marker words
(many short acts contain none) or the two dialects are mixed.
"""
import re

# Prefix matches: (ijekavian stem, ekavian stem). Prefixes are safe for these stems.
PAIRS = [
    ("vrijem", "vrem"), ("mjest", "mest"), ("rješen", "rešen"), ("rješav", "rešav"),
    ("primjen", "primen"), ("promjen", "promen"), ("izmjen", "izmen"),
    ("vrijed", "vred"), ("cjelin", "celin"), ("prijedlog", "predlog"),
    ("obavješt", "obavešt"), ("obavijest", "obaveštenj"),
    ("djelatn", "delatn"), ("djelokrug", "delokrug"), ("djelov", "delov"),
    ("dijelov", "delov"), ("sjedišt", "sedišt"), ("mjesec", "mesec"),
    ("bilježn", "beležn"), ("svjedo", "svedo"), ("procjen", "procen"),
    ("ocjen", "ocen"), ("zahtjev", "zahtev"), ("savjet", "savet"),
    ("vijeć", "već"), ("sljedeć", "sledeć"), ("tjelesn", "telesn"),
    ("izvješt", "izvešt"), ("dosljedn", "dosledn"), ("smjernic", "smernic"),
    ("uvjerenj", "uverenj"), ("ljekar", "lekar"),
    ("sjednic", "sednic"), ("predsjed", "predsed"), ("potpredsjed", "potpredsed"),
    ("cjelokup", "celokup"), ("mjerila", "merila"),
]
# "već" would match the comparative "veći" / "već" -> drop it from the ekavian side
PAIRS = [(i, e) for i, e in PAIRS if e != "već"] + [("vijeć", "")]  # "" = no ekavian prefix

# Whole-word matches (the ekavian side is too ambiguous as a prefix)
IJE_WORDS = {
    "gdje", "uvijek", "dvije", "svijet", "svijeta", "svijetu", "mjera", "mjere", "mjeri",
    "mjeru", "mjerom", "mjerama", "tijelo", "tijela", "tijelu", "tijelom", "tijelima",
    "cijena", "cijene", "cijeni", "cijenu", "cijenom", "cijenama", "vijeće", "vijeća",
    "vijeću", "vijećem",
}
EKA_WORDS = {
    "gde", "uvek", "dve", "svet", "sveta", "svetu", "mera", "mere", "meri", "meru",
    "merom", "merama", "telo", "tela", "telu", "telom", "telima",
    "cena", "cene", "ceni", "cenu", "cenom", "cenama", "veće", "veća", "veću", "većem",
}

_WORD = re.compile(r"\w+", re.UNICODE)
_IJE_PREFIX = tuple(i for i, _ in PAIRS if i)
_EKA_PREFIX = tuple(e for _, e in PAIRS if e)


def count_markers(text: str):
    ije = eka = 0
    for w in _WORD.findall(text.lower()):
        if w in IJE_WORDS:
            ije += 1
        elif w in EKA_WORDS:
            eka += 1
        elif w.startswith(_IJE_PREFIX):
            ije += 1
        elif w.startswith(_EKA_PREFIX):
            eka += 1
    return ije, eka


def detect_dialect(text: str, min_hits: int = 2, ratio: float = 2.0) -> str:
    ije, eka = count_markers(text)
    if ije + eka < min_hits:
        return "unknown"
    if ije >= ratio * eka:
        return "ijekavian"
    if eka >= ratio * ije:
        return "ekavian"
    return "unknown"  # mixed
