| Date | Member | Tool | Where | How | Result |
|---|---|---|---|---|---|
  | 03.11.2026 | Nejra Zurapi | Claude | src/transliterate.py | Claude generated the Serbian Cyrillic-to-Latin transliteration module as part of the project code kit | Used as provided; not modified |
| 03.11.2026 | Nejra Zurapi | Claude | src/dialect.py | Claude generated the ekavian/ijekavian detector (word-stem counting) as part of the project code kit | Used as provided; not modified |
| 06.11.2026 | Nejra Zurapi | Claude | src/clean.py | Claude generated the shared text-cleaning module (Unicode normalisation, removal of page numbers and gazette headers, title guessing, and script and dialect tagging) as part of the project code kit | Used as provided; not modified |
| 06.11.2026 | Nejra Zurapi | Claude | src/collect.py | Claude generated the collection script that downloads legal acts from a URL list (HTML and PDF), caches them, extracts the text and writes JSONL, as part of the project code kit | Used as provided; not modified |
| 06.11.2026 | Nejra Zurapi | Claude | src/common.py | Claude generated the shared constants and helpers (JSONL record format, the 10-area taxonomy, the EUROVOC domain mapping, read and write functions) as part of the project code kit | Modified by me: adapted the cleaning rules to the page layout of the portals I collected from |
