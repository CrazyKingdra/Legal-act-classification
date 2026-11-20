## Nejra Zurapi: 

**Data collection**
- Built the URL lists `data/raw/urls_bs.csv` (207 acts, Službeni glasnik BiH) and `data/raw/urls_sr.csv` (234 acts, Pravno-informacioni sistem RS) by hand, using each portal's search. 
- Chose acts across years and act types (zakon, uredba, pravilnik, odluka) and across the 10 legal areas. 
- Ran `src.collect` for both countries. Read the `*.failed.tsv` logs and replaced scanned PDFs and failed URLs with other acts.
- Spot-checked records for clean text, correct script and correct dialect detection.

**Test-set sampling**
- Ran `src.sample_test` for Bosnian, Serbian (with `--balance-script`) and Croatian, 100 acts each, seed 13.
- Checked the weak-label distribution, found thin areas (for example economy, education, agriculture and transport) and added more acts for them, then resampled.
- Shared the three `test_*_unlabelled.jsonl` files with the team.

**Annotation**
* Annotated `sheet_B.csv`, about 300 acts across Croatian, Bosnian and Serbian independently, following `docs/annotation_guidelines.md`: one of the 10 areas per act, a confidence score from 1 to 3, and a short note for borderline acts. 
