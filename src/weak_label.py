"""Keyword-based weak labels for national acts.

Used for two things only:
  1. stratifying the test-set sample so every area is represented, and
  2. optionally, extra (noisy) Croatian training data from Narodne novine.
Weak labels are NEVER used as gold test labels; those come from annotation.

Patterns are lower-case Latin stems covering Croatian, Bosnian and Serbian variants.
"""
import re
from collections import Counter

from .common import AREAS

KEYWORDS = {
    "finance_tax": ["porez", "poresk", "carin", "proračun", "budžet", "akciz", "trošarin",
                    "bank", "financij", "finansij", "računovodstv", "revizij", "devizn",
                    "kredit", "osiguranj", "vrijednosn papir", "hartij", "fiskal"],
    "social_labour": ["radn", "o radu", "zapošljav", "zaposlen", "mirovin", "penzij", "socijaln",
                      "zdravstv", "invalid", "rodilj", "porodilj", "boračk", "branitelj",
                      "nezaposlen", "štrajk", "plać", "doprinos"],
    "education_culture_science": ["obrazovanj", "škol", "visokom obraz", "sveučilišt", "univerzitet",
                                  "znanost", "nauk", "kultur", "medij", "autorsk", "sport",
                                  "elektroničk komunikac", "elektronsk komunikac", "knjižnic",
                                  "bibliotek", "arhiv"],
    "transport": ["promet", "saobraćaj", "cest", "željezni", "železni", "zračn", "vazdušn",
                  "pomorsk", "prijevoz", "prevoz", "vozil", "plovidb", "luk"],
    "environment_energy": ["okoliš", "životne sredine", "zaštit prirod", "energ", "električn",
                           "plin", "nafte", "vodama", "klim", "otpad", "emisij"],
    "agriculture_food": ["poljoprivred", "šum", "ribar", "ribolov", "veterinar", "hrane", "hrani",
                         "stočar", "sjemen", "semen", "biljn", "lovstv", "lovu"],
    "industry_technology": ["industrij", "rudar", "gradnj", "građevin", "tehničk", "standardizac",
                            "mjeriteljstv", "metrolog", "akreditac", "eksploziv", "proizvod"],
    "economy_trade_business": ["trgov", "privred", "gospodars", "trgovačk društv", "privredn društv",
                               "tržišn", "konkurencij", "natjecanj", "stečaj", "investic",
                               "javn nabav", "potrošač", "turiz", "obrt", "zanat"],
    "law_justice": ["kazn", "krivičn", "sud", "prekršaj", "parnič", "ovrh", "izvršn postup",
                    "javnobilježn", "notar", "odvjetn", "advokat", "zatvor", "policij", "obvez",
                    "obligac", "vlasništv", "svojin", "nasljeđ", "nasleđ", "obitelj", "porodic",
                    "upravn postup", "državljanstv", "zaštit podataka"],
    "politics_international": ["izbor", "vlad", "predsjedni", "predsedni", "skupštin", "sabor",
                               "ustav", "referendum", "međunarodn", "sporazum", "ratifik",
                               "potvrđivanj", "diplomat", "obran", "odbran", "vojsk",
                               "državn službenik", "lokaln samouprav", "ministarstv"],
}
assert set(KEYWORDS) == set(AREAS)
_PATTERNS = {a: [re.compile(r"\b" + re.escape(k)) for k in ks] for a, ks in KEYWORDS.items()}


def weak_label(title: str, text: str, head_chars: int = 3000):
    """Return (area, score) or (None, 0). Title matches count three times."""
    title, head = (title or "").lower(), (text or "")[:head_chars].lower()
    scores = Counter()
    for area, pats in _PATTERNS.items():
        for p in pats:
            scores[area] += 3 * len(p.findall(title)) + len(p.findall(head))
    if not scores or scores.most_common(1)[0][1] == 0:
        return None, 0
    area, score = scores.most_common(1)[0]
    return area, score
