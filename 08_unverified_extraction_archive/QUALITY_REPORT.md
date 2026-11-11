# EcoFlow-Optima data preparation report

Prepared 2026-11-02. This is an initial reproducible cleaning release, not a fully validated modeling dataset.

## What is included

- 56 unique source PDFs, 539 pages, unchanged from the browser download collection.
- 52 quarterly lake/tributary reports, one 2009-2012 annual report, and three special reports.
- All 56 PDFs have an extraction inventory. 238 candidate table/grid regions were detected. Chart grids can also appear in this archive and are not automatically accepted as observations.
- 10,401 extracted/transcribed parameter cells from 42 reports. This is not a count of independent samples.
- 2,175 exact numeric cells passing structural checks or explicit visual checking, arranged into 813 station-month rows.
- 96 cells explicitly checked visually: lake BOD and DO, all 16 listed stations, April-June 2026.
- 7,156 measurement records and 1133 table-level items remain flagged for review. A single cell can have multiple flags.

## Files and use

- `measurements_all.csv`: complete standardized extraction ledger, including uncertain values, source coordinates, raw tokens, censoring and quality flags. Do not train directly on this ledger.
- `measurements_structural_checks_passed.csv`: exact numeric subset for initial exploration. Most rows are source-text extraction with structural checks, not independently visually verified.
- `station_month_initial_eda.csv`: wide station-month version of that subset. Blank cells remain unavailable and are not zero. Units are in parameter_dictionary.csv.
- `measurement_review_queue.csv` and `table_review_queue.csv`: unresolved measurement and table problems.
- `report_inventory.csv`, `page_inventory.csv`, and `monthly_coverage_calendar.csv`: source/extraction coverage. Missing extraction is different from a missing source sample.
- `data_dictionary.csv`, `parameter_dictionary.csv`, `station_dictionary.csv`: field meanings and identifiers.
- `correction_log.csv` and `cleaning_log.csv`: explicit visual corrections and processing steps.
- Extracted page text, table matrices, OCR images, and cell geometry are retained under data/extracted/llda_2026-11-02.

## Cleaning decisions

1. Keep lake and tributary identities distinct. Do not infer geographic zones or coordinates.
2. Keep total coliform and fecal coliform distinct. Keep phosphate and inorganic phosphate distinctions where recoverable. Nutrient chemical mass basis is not inferred.
3. Normalize month keys and numeric notation. Do not invent sampling dates or publication timestamps.
4. Preserve limits such as <0.1 as an operator and bound. Leave numeric_value blank for censored values.
5. Preserve original missing symbols. An OCR blank is not proof that the agency did not sample.
6. Keep duplicate keys for review. Do not silently average, choose a preferred report, or discard competing values.
7. Quarantine OCR results until visually checked. OCR scores are heuristic and cannot prove correctness. Missing decimal points can produce plausible but wrong values.
8. Values outside broad physical checks are flags, not automatic deletions or fish-kill labels. Valid extremes are retained in the ledger.
9. Do not combine annual/special-lake summaries with monthly Laguna de Bay observations. The annual 2009-2012 report remains supplemental, with text preserved but no monthly table extraction performed in this release.
10. Exclude tables whose recovered month headings disagree with the filename quarter. In particular, the 2014 Q1 PDF includes appended April-June tables; their historical period must be independently resolved before merging.

## Source and extraction gaps

2014 Q3 and 2020 Q2 are unavailable from the source page. Links labeled 2026 Q3/Q4 are broken and point toward 2025 filenames. The source page is https://llda.gov.ph/ldb-and-its-tributaries/.

Reports with no mapped monthly measurements in this release (not proof of no observations):

- 2014q4.pdf
- 2015q1.pdf
- 2015q3.pdf
- 2015q4.pdf
- 2017q2.pdf
- 2017q3.pdf
- 2018q1.pdf
- 2020q3.pdf
- 2022q2.pdf
- 2022q4.pdf
- AWQR_2009-2012.pdf
- Sapang_Baho-Q4-2021.pdf
- Taguig_River-Q1-2022.pdf
- WQR-Tadlac Lake_2020.pdf

No-grid detection, unresolved headers, merged cells and station labels remain in the table review queue. Chloride and total suspended solids are visible in the inspected 2026 Q2 source table but have not been reliably mapped into the standardized ledger in this release. Their absence from the CSV is an extraction gap, not an absence of agency measurements. Some tables continue onto another page; unmapped continuation rows must be checked before claiming complete station coverage.

## What remains before selecting an ML task

Complete review of the actual measurement tables, resolve extraction gaps and duplicate/period conflicts, and then calculate station/parameter coverage and genuine consecutive-month histories. Establish observation availability times before defining a prospective forecast. This release does not justify selecting a model, claiming fish-kill probabilities, estimating carrying capacity, or recommending gate operations.

## Reproduction

Run scripts/data_preparation/extract_reports.py, clean_reports.py, and document_dataset.py with the bundled Python runtime. Extraction requires the local task OCR environment under tmp/tesseract_env and the local OCR helper dependencies under tmp/ocr_deps. Extraction caches are versioned. Review transcriptions are in scripts/data_preparation/verified_2026_q2.json. Original source hashes are checked during documentation generation.
