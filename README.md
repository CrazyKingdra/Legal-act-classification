# Cross-lingual legal act classification (HR → BS / SR)

Train on Croatian legal acts, test on Bosnian and Serbian acts. This repository contains
everything from data collection to the final results tables.

## Setup

```bash
pip install -r requirements.txt
```
Fine-tuning (`src/finetune.py`) needs a GPU; a free Colab T4 is enough. Everything else
runs on a laptop. Run all commands from the repository root.

## Pipeline at a glance

```
MultiEURLEX (hr) ──prepare_multieurlex──► train/validation_eurlex_hr.jsonl ─┐
Narodne novine ──collect──► hr_national ──sample_test──► test_hr_unlabelled ┤
Sl. glasnik BiH ─collect──► bs ─────────sample_test──► test_bs_unlabelled ──┤
PIS Srbije ──────collect──► sr ─────────sample_test──► test_sr_unlabelled ──┤
                                                                            ▼
                                    annotation sheets → agree → merge → test_{hr,bs,sr}.jsonl
                                                                            ▼
                                       baseline.py / finetune.py → results/<model>/*.jsonl
                                                                            ▼
                                                    evaluate.py → results/summary.md
```

## Who does what, in order

### Phase 1: data

**Member 1: Croatian data and taxonomy**
1. `python -m src.prepare_multieurlex inspect`
   This writes `data/interim/label_map.csv`. Check that all 21 EUROVOC domains have a name
   and an area. Fill any blanks by hand (use `ignore` for Geography).
2. `python -m src.prepare_multieurlex build`
   This writes the training, validation and test files and `eurlex_stats.json`. Check how
   many acts were dropped as ties. If more than about 40% were dropped, rerun with
   `--tie-break first`.
3. Read `docs/annotation_guidelines.md` and adjust it if the team disagrees with any decision.
   It must be final before annotation starts.
4. Collect about 250 Croatian national acts from Narodne novine. Use the portal's search to
   list act URLs in `data/raw/urls_hr.csv` (format described in `src/collect.py`), spread
   across years and act types (zakon, uredba, pravilnik). Add the Croatian copyright act
   with `parallel_group=copyright`. Then run:
   `python -m src.collect data/raw/urls_hr.csv --out data/interim/hr_national.jsonl`
5. Run `python -m src.sample_test data/interim/hr_national.jsonl --n 100 --out data/processed/test_hr_unlabelled.jsonl`

**Member 2: Bosnian and Serbian data**
1. List about 250 act URLs each in `data/raw/urls_bs.csv` (Službeni glasnik BiH) and
   `data/raw/urls_sr.csv` (Pravno-informacioni sistem RS). For Serbian, make sure both
   Cyrillic and Latin versions are present. Add the copyright acts with
   `parallel_group=copyright`. Check each portal's terms of use and robots.txt first.
2. Run:
   ```bash
   python -m src.collect data/raw/urls_bs.csv --out data/interim/bs.jsonl
   python -m src.collect data/raw/urls_sr.csv --out data/interim/sr.jsonl
   ```
   Check the `*.failed.tsv` logs. Scanned PDFs yield no text; replace them with other acts.
3. Open about 10 records from each file and check that the text is clean and that
   `script` and `dialect` were detected correctly.
4. Sample the test sets:
   ```bash
   python -m src.sample_test data/interim/bs.jsonl --n 100 --out data/processed/test_bs_unlabelled.jsonl
   python -m src.sample_test data/interim/sr.jsonl --n 100 --balance-script --out data/processed/test_sr_unlabelled.jsonl
   ```

**Member 3: modelling**
Start as soon as Member 1 finishes step 2. You can run the baseline against MultiEURLEX's
own test split while the national test sets are being annotated:
```bash
python -m src.baseline --name tfidf_char_lr --features char --clf lr
```
Set up the Colab notebook and fine-tune BERTić once (see Phase 3) to estimate run time.

### Phase 2: annotation (Members 1 and 2 annotate, Member 3 adjudicates)

```bash
python -m src.annotation sheets     # data/annotation/sheet_A.csv (Member 1), sheet_B.csv (Member 2)
```
Each annotator fills the `label` and `confidence` columns **independently**, following the
guidelines. Expect about 300 acts at 2–3 minutes each, so roughly 12 hours per person.
```bash
python -m src.annotation agree      # prints Cohen's kappa, writes disagreements.csv
```
Member 3 fills `final_label` in `disagreements.csv`, then:
```bash
python -m src.annotation merge      # writes data/processed/test_{hr,bs,sr}.jsonl
```
Kappa above 0.6 is acceptable. If it's lower, discuss the disagreements, clarify the
guidelines, and re-annotate.

### Phase 3: experiments (Member 3)

```bash
# Baselines
python -m src.baseline --name tfidf_char_lr  --features char --clf lr
python -m src.baseline --name tfidf_char_svm --features char --clf svm
python -m src.baseline --name tfidf_word_lr  --features word --clf lr

# Transformers (GPU)
python -m src.finetune --name bertic_chunk --model classla/bcms-bertic --mode chunk
python -m src.finetune --name bertic_first --model classla/bcms-bertic --mode first
python -m src.finetune --name xlmr_chunk   --model xlm-roberta-base   --mode chunk

# RQ3: Serbian without transliteration (Cyrillic stays Cyrillic)
python -m src.baseline --name tfidf_char_lr --load --test data/processed/test_sr.jsonl --text-field text_orig
python -m src.finetune --name bertic_chunk  --load --test data/processed/test_sr.jsonl --text-field text_orig
```
On Colab: upload the repository, `pip install -r requirements.txt`, then run the commands
above in cells prefixed with `!`. Download `results/` afterwards. If you run out of GPU
memory, use `--batch 8`. For 3 epochs on MultiEURLEX-hr with chunking, expect a few hours
on a T4; lower `--max-train-chunks` to 2 to halve that.

### Phase 4: evaluation and report

```bash
python -m src.evaluate     # Member 2
```
This writes `results/summary.md` with every table the report needs: macro-F1 with CIs,
accuracy, the script and dialect subsets (RQ3), the cross-lingual drop (RQ2), per-class F1,
and the parallel-acts table. Each model folder also gets `errors_*.csv` and
`confusion_*.csv` for the error analysis.

| Report section | Owner | Source |
|---|---|---|
| Data and annotation (incl. kappa) | Member 1 | `eurlex_stats.json`, `data/annotation/agreement.json` |
| Methods and results (RQ1–RQ3) | Member 3 | `results/summary.md` |
| Error analysis | Member 2 | `results/*/errors_*.csv`, `confusion_*.csv` |
| Parallel-acts case study | Member 3 | parallel table in `summary.md` |
| Compiling and editing | Member 1 | |

## Mapping to research questions

- **RQ1:** macro-F1 on `test_hr` (Croatian national acts). Also report `test_eurlex_hr` to
  show the EU→national domain gap.
- **RQ2:** macro-F1 on `test_bs` and `test_sr`, and the `drop_hr_to_*` rows.
- **RQ3:** `test_sr` vs. `test_sr__orig` (transliteration effect), plus the
  `script=` and `dialect=` subset rows.

## What has and hasn't been tested

Every script except `finetune.py`'s training loop was run end to end on synthetic data:
collection/cleaning utilities, transliteration, dialect detection, sampling, the annotation
workflow, both baselines and evaluation. `finetune.py`'s chunking and data encoding were
tested with a stand-in tokenizer. The training loop itself needs PyTorch and the
downloaded models, so run it on a small subset first, e.g. `--epochs 0.1`, before the
full run.
