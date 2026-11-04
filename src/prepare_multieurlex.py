"""Member 1, step 1: build the Croatian training set from MultiEURLEX.

Usage:
  python -m src.prepare_multieurlex inspect     # writes data/interim/label_map.csv for review
  python -m src.prepare_multieurlex build       # writes data/processed/train_eurlex_hr.jsonl etc.

`inspect` resolves the 21 EUROVOC level-1 label ids to English names and fills
in the coarse area from common.EUROVOC_DOMAIN_TO_AREA. Open the CSV, check every
row, and fix the `area` column by hand if anything did not resolve.
`build` then gives every act the single area that most of its labels belong to.
"""
import argparse
import csv
import json
from collections import Counter

from .common import AREAS, DATA, EUROVOC_DOMAIN_TO_AREA, write_jsonl

LABEL_MAP = DATA / "interim" / "label_map.csv"


def load(split):
    from datasets import load_dataset
    return load_dataset("coastalcph/multi_eurlex", "hr", label_level="level_1",
                        split=split, trust_remote_code=True)


def eurovoc_names():
    """Return {eurovoc_id: English name} using the descriptor file in the dataset repo."""
    try:
        from huggingface_hub import hf_hub_download
        path = hf_hub_download("coastalcph/multi_eurlex", "eurovoc_descriptors.json",
                               repo_type="dataset")
        desc = json.load(open(path, encoding="utf-8"))
        return {k: (v.get("en") if isinstance(v, dict) else v) for k, v in desc.items()}
    except Exception as e:  # noqa: BLE001
        print(f"[warn] could not load EUROVOC descriptors ({e}); fill names by hand")
        return {}


def inspect():
    ds = load("train")
    ids = ds.features["labels"].feature.names
    names = eurovoc_names()
    LABEL_MAP.parent.mkdir(parents=True, exist_ok=True)
    with open(LABEL_MAP, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["index", "eurovoc_id", "name", "area"])
        for i, eid in enumerate(ids):
            name = (names.get(eid) or "").upper().strip()
            area = EUROVOC_DOMAIN_TO_AREA.get(name, "")
            w.writerow([i, eid, name, "" if area is None else area])
    print(f"wrote {LABEL_MAP}. Check it: every row needs an area (or 'ignore').")


def read_label_map():
    m = {}
    with open(LABEL_MAP, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            area = row["area"].strip()
            if area and area != "ignore":
                assert area in AREAS, f"unknown area {area!r} in {LABEL_MAP}"
                m[int(row["index"])] = area
    return m


def majority_area(label_idx, idx2area, tie_break):
    areas = [idx2area[i] for i in label_idx if i in idx2area]
    if not areas:
        return None
    counts = Counter(areas).most_common()
    if len(counts) > 1 and counts[0][1] == counts[1][1]:
        # tie: either drop, or take the first label listed among the tied areas
        if tie_break == "drop":
            return None
        tied = {a for a, c in counts if c == counts[0][1]}
        return next(a for a in areas if a in tied)
    return counts[0][0]


def build(tie_break):
    idx2area = read_label_map()
    stats = {}
    for split in ["train", "validation", "test"]:
        rows, dropped = [], 0
        for ex in load(split):
            area = majority_area(ex["labels"], idx2area, tie_break)
            if area is None:
                dropped += 1
                continue
            rows.append({
                "id": f"eurlex-{ex['celex_id']}", "lang": "hr", "source": "multieurlex",
                "title": "", "text": ex["text"], "text_orig": ex["text"],
                "script": "latin", "dialect": "ijekavian", "label": area,
                "url": f"https://eur-lex.europa.eu/legal-content/HR/TXT/?uri=CELEX:{ex['celex_id']}",
            })
        write_jsonl(rows, DATA / "processed" / f"{split}_eurlex_hr.jsonl")
        stats[split] = {"kept": len(rows), "dropped": dropped,
                        "per_area": dict(Counter(r["label"] for r in rows))}
    json.dump(stats, open(DATA / "processed" / "eurlex_stats.json", "w"), indent=2)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["inspect", "build"])
    ap.add_argument("--tie-break", choices=["drop", "first"], default="drop")
    a = ap.parse_args()
    inspect() if a.cmd == "inspect" else build(a.tie_break)
