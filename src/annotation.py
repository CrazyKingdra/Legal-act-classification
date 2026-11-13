"""Double annotation workflow (Members 1 and 2 annotate, Member 3 adjudicates).

  python -m src.annotation sheets      # makes data/annotation/sheet_A.csv and sheet_B.csv
  # annotators fill the `label` column independently (open the url to read the full act)
  python -m src.annotation agree       # Cohen's kappa + data/annotation/disagreements.csv
  # Member 3 fills `final_label` in disagreements.csv
  python -m src.annotation merge       # writes data/processed/test_{hr,bs,sr}.jsonl with gold labels
"""
import argparse
import csv
import json
import random
from collections import defaultdict

from .common import AREAS, DATA, read_jsonl, write_jsonl

ANN = DATA / "annotation"
LANGS = ["hr", "bs", "sr"]
FIELDS = ["id", "lang", "title", "url", "text_preview", "label", "confidence", "note"]


def unlabelled():
    rows = []
    for lang in LANGS:
        p = DATA / "processed" / f"test_{lang}_unlabelled.jsonl"
        if p.exists():
            rows += read_jsonl(p)
    return rows


def sheets(preview_chars):
    rows = unlabelled()
    ANN.mkdir(parents=True, exist_ok=True)
    for who, seed in [("A", 1), ("B", 2)]:
        rs = rows[:]
        random.Random(seed).shuffle(rs)  # different order reduces ordering effects
        with open(ANN / f"sheet_{who}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, FIELDS)
            w.writeheader()
            for r in rs:
                w.writerow({"id": r["id"], "lang": r["lang"], "title": r["title"], "url": r["url"],
                            "text_preview": r["text"][:preview_chars].replace("\n", " "),
                            "label": "", "confidence": "", "note": ""})
    print(f"wrote {len(rows)} rows to sheet_A.csv and sheet_B.csv in {ANN}")
    print("Allowed labels:", ", ".join(AREAS))


def read_sheet(who):
    out, bad = {}, []
    with open(ANN / f"sheet_{who}.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lab = r["label"].strip()
            if lab not in AREAS:
                bad.append((r["id"], lab))
            out[r["id"]] = r
    if bad:
        print(f"[sheet_{who}] {len(bad)} rows have a missing/invalid label, e.g. {bad[:3]}")
    return out


def agree():
    from sklearn.metrics import cohen_kappa_score
    A, B = read_sheet("A"), read_sheet("B")
    ids = [i for i in A if i in B and A[i]["label"] in AREAS and B[i]["label"] in AREAS]
    report = {}
    groups = defaultdict(list)
    for i in ids:
        groups["all"].append(i)
        groups[A[i]["lang"]].append(i)
    for g, gids in groups.items():
        a = [A[i]["label"] for i in gids]
        b = [B[i]["label"] for i in gids]
        report[g] = {"n": len(gids),
                     "raw_agreement": round(sum(x == y for x, y in zip(a, b)) / len(gids), 3),
                     "cohen_kappa": round(cohen_kappa_score(a, b), 3)}
    print(json.dumps(report, indent=2))
    json.dump(report, open(ANN / "agreement.json", "w"), indent=2)

    dis = [i for i in ids if A[i]["label"] != B[i]["label"]]
    with open(ANN / "disagreements.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "lang", "title", "url", "label_A", "note_A", "label_B", "note_B", "final_label"])
        for i in dis:
            w.writerow([i, A[i]["lang"], A[i]["title"], A[i]["url"], A[i]["label"], A[i]["note"],
                        B[i]["label"], B[i]["note"], ""])
    print(f"{len(dis)} disagreements -> {ANN / 'disagreements.csv'} (Member 3 fills final_label)")


def merge():
    A, B = read_sheet("A"), read_sheet("B")
    final = {}
    p = ANN / "disagreements.csv"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["final_label"].strip() in AREAS:
                    final[r["id"]] = r["final_label"].strip()
    for lang in LANGS:
        src = DATA / "processed" / f"test_{lang}_unlabelled.jsonl"
        if not src.exists():
            continue
        out, missing = [], []
        for r in read_jsonl(src):
            a, b = A.get(r["id"], {}).get("label"), B.get(r["id"], {}).get("label")
            lab = a if (a == b and a in AREAS) else final.get(r["id"])
            if lab is None:
                missing.append(r["id"])
                continue
            r["label"] = lab
            out.append(r)
        write_jsonl(out, DATA / "processed" / f"test_{lang}.jsonl")
        if missing:
            print(f"[{lang}] {len(missing)} acts still unresolved, e.g. {missing[:3]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sheets", "agree", "merge"])
    ap.add_argument("--preview-chars", type=int, default=1500)
    a = ap.parse_args()
    {"sheets": lambda: sheets(a.preview_chars), "agree": agree, "merge": merge}[a.cmd]()
