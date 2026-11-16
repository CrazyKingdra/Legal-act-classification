"""python -m src.evaluate

For every model and test set it reports macro-F1, accuracy and per-class F1 with 95%
bootstrap confidence intervals, plus subsets by script and dialect. It also reports the
cross-lingual drop (macro-F1 on test_hr minus test_bs / test_sr) with a bootstrap CI,
and writes per-model confusion matrices and error lists for the error analysis.

Outputs: results/summary.md, results/summary.json, results/<model>/errors_<test>.csv,
         results/<model>/confusion_<test>.csv
"""
import argparse
import csv
import json
from collections import defaultdict

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from .common import AREAS, DATA, RESULTS, read_jsonl


def macro_f1(y, p):
    return f1_score(y, p, labels=AREAS, average="macro", zero_division=0)


def bootstrap(y, p, fn, n=1000, seed=0):
    rng = np.random.default_rng(seed)
    y, p = np.array(y), np.array(p)
    vals = [fn(y[i], p[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(n))]
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def bootstrap_drop(ya, pa, yb, pb, n=1000, seed=0):
    """CI for macro-F1(a) - macro-F1(b), resampling the two test sets independently."""
    rng = np.random.default_rng(seed)
    ya, pa, yb, pb = map(np.array, (ya, pa, yb, pb))
    d = []
    for _ in range(n):
        i = rng.integers(0, len(ya), len(ya))
        j = rng.integers(0, len(yb), len(yb))
        d.append(macro_f1(ya[i], pa[i]) - macro_f1(yb[j], pb[j]))
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def score(y, p, n_boot):
    lo, hi = bootstrap(y, p, macro_f1, n_boot)
    per = f1_score(y, p, labels=AREAS, average=None, zero_division=0)
    return {"n": len(y), "macro_f1": round(macro_f1(y, p), 4), "macro_f1_ci": [round(lo, 4), round(hi, 4)],
            "accuracy": round(accuracy_score(y, p), 4),
            "per_class_f1": {a: round(float(f), 4) for a, f in zip(AREAS, per)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--min-subset", type=int, default=15, help="skip subsets smaller than this")
    a = ap.parse_args()

    gold = {}
    for f in sorted((DATA / "processed").glob("test_*.jsonl")):
        if "unlabelled" in f.stem:
            continue
        gold[f.stem] = {r["id"]: r for r in read_jsonl(f)}
    if not gold:
        raise SystemExit("no gold test sets in data/processed/ (run src.annotation merge first)")

    summary = defaultdict(dict)
    raw = defaultdict(dict)
    for mdir in sorted(p for p in RESULTS.iterdir() if p.is_dir()):
        for pf in sorted(mdir.glob("test_*.jsonl")):
            test = pf.stem.split("__")[0]
            if test not in gold:
                continue
            preds = {r["id"]: r["pred"] for r in read_jsonl(pf)}
            ids = [i for i in gold[test] if i in preds]
            if len(ids) < len(gold[test]):
                print(f"[warn] {mdir.name}/{pf.name}: {len(gold[test]) - len(ids)} gold acts lack predictions")
            G = gold[test]
            y = [G[i]["label"] for i in ids]
            p = [preds[i] for i in ids]
            res = score(y, p, a.n_boot)
            # subsets: script and dialect
            subsets = {}
            for key in ("script", "dialect"):
                groups = defaultdict(list)
                for k, i in enumerate(ids):
                    groups[G[i].get(key, "unknown")].append(k)
                if len(groups) > 1:
                    for val, ks in groups.items():
                        if len(ks) >= a.min_subset:
                            subsets[f"{key}={val}"] = score([y[k] for k in ks], [p[k] for k in ks], a.n_boot)
            res["subsets"] = subsets
            summary[mdir.name][pf.stem] = res
            raw[mdir.name][pf.stem] = (y, p)

            cm = confusion_matrix(y, p, labels=AREAS)
            with open(mdir / f"confusion_{pf.stem}.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["gold\\pred"] + AREAS)
                for a_, row in zip(AREAS, cm):
                    w.writerow([a_] + list(row))
            with open(mdir / f"errors_{pf.stem}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["id", "title", "gold", "pred", "script", "dialect", "parallel_group", "url"])
                for i, yy, pp in zip(ids, y, p):
                    if yy != pp:
                        g = G[i]
                        w.writerow([i, g.get("title", ""), yy, pp, g.get("script"), g.get("dialect"),
                                    g.get("parallel_group") or "", g.get("url", "")])

        # cross-lingual drop relative to Croatian
        if "test_hr" in raw[mdir.name]:
            yh, ph = raw[mdir.name]["test_hr"]
            for t in ("test_bs", "test_sr", "test_sr__orig"):
                if t in raw[mdir.name]:
                    yt, pt = raw[mdir.name][t]
                    drop = macro_f1(yh, ph) - macro_f1(yt, pt)
                    lo, hi = bootstrap_drop(yh, ph, yt, pt, a.n_boot)
                    summary[mdir.name][f"drop_hr_to_{t[5:]}"] = {"macro_f1_drop": round(drop, 4),
                                                                 "ci": [round(lo, 4), round(hi, 4)]}

    # parallel acts case study
    parallel = defaultdict(dict)
    for m, tests in raw.items():
        for t in tests:
            if "__" in t:
                continue
            preds = {r["id"]: r["pred"] for r in read_jsonl(RESULTS / m / f"{t}.jsonl")}
            for i, g in gold.get(t, {}).items():
                if g.get("parallel_group") and i in preds:
                    parallel[g["parallel_group"]][(m, g["lang"])] = (g["label"], preds[i])

    json.dump({"models": summary, "parallel": {k: {f"{m}|{l}": v for (m, l), v in d.items()}
                                               for k, d in parallel.items()}},
              open(RESULTS / "summary.json", "w"), indent=2)
    write_markdown(summary, parallel)


def write_markdown(summary, parallel):
    L = ["# Results\n", "## Macro-F1 [95% bootstrap CI] and accuracy\n",
         "| model | test | n | macro-F1 | 95% CI | accuracy |", "|---|---|---|---|---|---|"]
    for m, tests in summary.items():
        for t, r in tests.items():
            if t.startswith("drop"):
                continue
            L.append(f"| {m} | {t} | {r['n']} | {r['macro_f1']:.3f} | {r['macro_f1_ci'][0]:.3f}–{r['macro_f1_ci'][1]:.3f} | {r['accuracy']:.3f} |")
            for s, sr in r["subsets"].items():
                L.append(f"| {m} | {t} ({s}) | {sr['n']} | {sr['macro_f1']:.3f} | {sr['macro_f1_ci'][0]:.3f}–{sr['macro_f1_ci'][1]:.3f} | {sr['accuracy']:.3f} |")
    L += ["\n## Cross-lingual drop (macro-F1 on Croatian minus target)\n",
          "| model | target | drop | 95% CI |", "|---|---|---|---|"]
    for m, tests in summary.items():
        for t, r in tests.items():
            if t.startswith("drop"):
                L.append(f"| {m} | {t.replace('drop_hr_to_', '')} | {r['macro_f1_drop']:.3f} | {r['ci'][0]:.3f}–{r['ci'][1]:.3f} |")
    L += ["\n## Per-class F1\n", "| model | test | " + " | ".join(AREAS) + " |",
          "|---|---|" + "---|" * len(AREAS)]
    for m, tests in summary.items():
        for t, r in tests.items():
            if not t.startswith("drop"):
                L.append(f"| {m} | {t} | " + " | ".join(f"{r['per_class_f1'][a]:.2f}" for a in AREAS) + " |")
    if parallel:
        L += ["\n## Parallel acts (gold → predicted)\n", "| group | model | language | gold | predicted |",
              "|---|---|---|---|---|"]
        for g, d in parallel.items():
            for (m, lang), (gl, pr) in sorted(d.items()):
                L.append(f"| {g} | {m} | {lang} | {gl} | {pr}{'' if gl == pr else ' ✗'} |")
    (RESULTS / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {RESULTS / 'summary.md'} and summary.json")


if __name__ == "__main__":
    main()
