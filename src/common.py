"""Shared constants and helpers.

Every dataset in this project is a JSONL file with one act per line:
  id          unique id, e.g. "hr-nn-2021-111-1941"
  lang        "hr" | "bs" | "sr"
  source      "multieurlex" | "narodne-novine" | "sg-bih" | "pis-rs"
  title       act title (may be "")
  text        cleaned text, Latin script (used by all models)
  text_orig   cleaned text in its original script (for the RQ3 transliteration test)
  script      "latin" | "cyrillic"
  dialect     "ekavian" | "ijekavian" | "unknown"
  label       one of AREAS (missing until annotated)
  parallel_group  optional; same value for equivalent acts across countries
  url         where the act came from
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"

# Shared taxonomy: 10 coarse legal areas built from top-level EUROVOC domains.
# Definitions: docs/annotation_guidelines.md
AREAS = [
    "politics_international",
    "law_justice",
    "economy_trade_business",
    "finance_tax",
    "social_labour",
    "education_culture_science",
    "transport",
    "environment_energy",
    "agriculture_food",
    "industry_technology",
]
AREA2ID = {a: i for i, a in enumerate(AREAS)}

# EUROVOC level-1 domain (English name) -> coarse area.
# GEOGRAPHY is not a legal area and is ignored when assigning labels.
EUROVOC_DOMAIN_TO_AREA = {
    "POLITICS": "politics_international",
    "INTERNATIONAL RELATIONS": "politics_international",
    "EUROPEAN UNION": "politics_international",
    "INTERNATIONAL ORGANISATIONS": "politics_international",
    "LAW": "law_justice",
    "ECONOMICS": "economy_trade_business",
    "TRADE": "economy_trade_business",
    "BUSINESS AND COMPETITION": "economy_trade_business",
    "FINANCE": "finance_tax",
    "SOCIAL QUESTIONS": "social_labour",
    "EMPLOYMENT AND WORKING CONDITIONS": "social_labour",
    "EDUCATION AND COMMUNICATIONS": "education_culture_science",
    "SCIENCE": "education_culture_science",
    "TRANSPORT": "transport",
    "ENVIRONMENT": "environment_energy",
    "ENERGY": "environment_energy",
    "AGRICULTURE, FORESTRY AND FISHERIES": "agriculture_food",
    "AGRI-FOODSTUFFS": "agriculture_food",
    "PRODUCTION, TECHNOLOGY AND RESEARCH": "industry_technology",
    "INDUSTRY": "industry_technology",
    "GEOGRAPHY": None,
}


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows -> {path}")
