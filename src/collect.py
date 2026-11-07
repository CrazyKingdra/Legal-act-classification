"""Each portal has its own search interface and page layout, so we do not hard-code
a crawler. Instead, collect act URLs with each portal's own search (by year,
act type, or keyword) and list them in a CSV:

  url,lang,source,title,parallel_group
  https://narodne-novine.nn.hr/clanci/sluzbeni/2021_10_111_1941.html,hr,narodne-novine,Zakon o autorskom pravu i srodnim pravima,copyright
  https://.../some-act.pdf,bs,sg-bih,,

Usage:
  python -m src.collect data/raw/urls_bs.csv  --out data/interim/bs.jsonl
  python -m src.collect data/raw/urls_sr.csv  --out data/interim/sr.jsonl

Downloads are cached in data/raw/cache/, so re-running is cheap. A delay between
requests keeps us polite to the government servers; do not lower it much.
"""
import argparse
import csv
import hashlib
import io
import time

import requests

from .clean import clean_record
from .common import DATA, write_jsonl

CACHE = DATA / "raw" / "cache"
HEADERS = {"User-Agent": "Mozilla/5.0 (academic research project; legal act classification)"}


def fetch(url, delay):
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()
    hit = list(CACHE.glob(key + ".*"))
    if hit:
        return hit[0].read_bytes(), hit[0].suffix
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    ext = ".pdf" if ("pdf" in ctype or url.lower().endswith(".pdf")) else ".html"
    (CACHE / (key + ext)).write_bytes(r.content)
    time.sleep(delay)
    return r.content, ext


def extract_sluzbenilist(html: str) -> str:
    """sluzbenilist.ba keeps article headings in <p class="text-center"> and the article
    bodies as LOOSE text between those tags (followed by <br>). Generic extractors such
    as trafilatura drop that loose text, so read the whole container instead."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    heads = soup.select("p.text-center")
    if not heads:
        return ""
    # smallest ancestor of the first heading that also contains the last heading
    container = heads[0].parent
    while container is not None and heads[-1] not in container.descendants:
        container = container.parent
    if container is None:
        return ""
    for tag in container(["script", "style", "nav", "form", "button"]):
        tag.decompose()
    for br in container.find_all("br"):
        br.replace_with("\n")
    for tag in container.find_all(["p", "div", "tr", "li", "h1", "h2", "h3", "h4"]):
        tag.append("\n")
    for tag in container.find_all(["td", "th"]):
        tag.append(" | ")
    return container.get_text("")


def extract_trafilatura(html: str) -> str:
    import trafilatura
    text = trafilatura.extract(html, include_comments=False, include_tables=True,
                               favor_recall=True)
    return text or ""


def extract_text(content, ext, url=""):
    if ext == ".pdf":
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages)
    html = content.decode("utf-8", errors="replace")
    generic = extract_trafilatura(html)
    if "sluzbenilist.ba" in url:
        try:
            special = extract_sluzbenilist(html)
        except Exception:  # noqa: BLE001
            special = ""
        # keep the specialised result unless it clearly found less text
        if len(special) >= len(generic):
            return special
    return generic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls_csv")
    ap.add_argument("--out", required=True)
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between requests")
    ap.add_argument("--min-chars", type=int, default=500, help="drop extractions shorter than this")
    a = ap.parse_args()

    rows, failed = [], []
    with open(a.urls_csv, encoding="utf-8") as f:
        items = list(csv.DictReader(f))
    for n, it in enumerate(items, 1):
        url = it["url"].strip()
        try:
            content, ext = fetch(url, a.delay)
            text = extract_text(content, ext, url)
        except Exception as e:  # noqa: BLE001
            failed.append((url, str(e)))
            continue
        if len(text) < a.min_chars:
            failed.append((url, f"only {len(text)} chars extracted (scanned PDF?)"))
            continue
        rec = clean_record({
            "id": f"{it['lang']}-{it['source']}-{hashlib.sha1(url.encode()).hexdigest()[:10]}",
            "lang": it["lang"], "source": it["source"], "title": it.get("title", "") or "",
            "text": text, "url": url, "parallel_group": it.get("parallel_group") or None,
        })
        rows.append(rec)
        print(f"[{n}/{len(items)}] {rec['script']:8} {rec['dialect']:9} {len(rec['text']):>7} chars  {url}")
    write_jsonl(rows, a.out)
    if failed:
        log = a.out + ".failed.tsv"
        with open(log, "w", encoding="utf-8") as f:
            f.writelines(f"{u}\t{e}\n" for u, e in failed)
        print(f"{len(failed)} failures logged to {log}")


if __name__ == "__main__":
    main()
