"""
  python -m src.sample_test data/interim/bs.jsonl --n 100 --out data/processed/test_bs_unlabelled.jsonl
  python -m src.sample_test data/interim/sr.jsonl --n 100 --balance-script --out data/processed/test_sr_unlabelled.jsonl
  python -m src.sample_test data/interim/hr_national.jsonl --n 100 --out data/processed/test_hr_unlabelled.jsonl
"""
import argparse
import random
from collections import defaultdict

from .common import AREAS, read_jsonl, write_jsonl
from .weak_label import weak_label


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--balance-script", action="store_true",
                    help="alternate Cyrillic/Latin within each area (Serbian)")
    ap.add_argument("--exclude", nargs="*", default=[],
                    help="JSONL files whose ids must not be sampled (e.g. training data)")
    a = ap.parse_args()
    rng = random.Random(a.seed)

    excluded = {r["id"] for f in a.exclude for r in read_jsonl(f)}
    rows = [r for r in read_jsonl(a.input) if r["id"] not in excluded]
    chosen = [r for r in rows if r.get("parallel_group")]
    pool = [r for r in rows if not r.get("parallel_group")]

    buckets = defaultdict(list)
    for r in pool:
        area, _ = weak_label(r["title"], r["text"])
        r["weak_label"] = area
        buckets[area].append(r)
    for b in buckets.values():
        rng.shuffle(b)
        if a.balance_script:
            cyr = [r for r in b if r["script"] == "cyrillic"]
            lat = [r for r in b if r["script"] == "latin"]
            b[:] = [x for pair in zip(cyr, lat) for x in pair] + cyr[len(lat):] + lat[len(cyr):]

    # round-robin over areas until n acts are chosen
    order = AREAS + [None]
    while len(chosen) < a.n and any(buckets[k] for k in order):
        for k in order:
            if buckets[k] and len(chosen) < a.n:
                chosen.append(buckets[k].pop(0))

    for r in chosen:
        r.pop("label", None)  # gold labels come only from annotation
    write_jsonl(chosen, a.out)
    by_area = defaultdict(int)
    for r in chosen:
        by_area[r.get("weak_label")] += 1
    print("weak-label distribution of sample:", dict(by_area))
    if any(v < a.n // 20 for k, v in by_area.items() if k):
        print("[note] some areas are thin; collect more acts for them if you can")


if __name__ == "__main__":
    main()
