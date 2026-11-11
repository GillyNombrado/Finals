# EcoFlow Optima deliverables

Prepared 2 November 2026. Start here to choose the correct file.

## Main files

| Purpose | File | Contents |
| --- | --- | --- |
| Cleaned measurements for analysis | 01_cleaned_data/lake_numeric_analysis.csv | 3,384 exact source-reviewed BOD/DO values in long form |
| Calendar-aligned cleaned dataset | 01_cleaned_data/lake_station_month_calendar.csv | 16 stations by 162 months, including explicit missing and unavailable statuses; 2,592 calendar rows are not 2,592 sampled observations |
| All reviewed values including non-exact values | 01_cleaned_data/lake_measurements_reviewed_long.csv | 3,555 cells, including 24 censored, 146 source-missing and one unreadable value |
| Proposed supervised training dataset | 02_training_candidate/training_do_next_month.csv | 1,430 complete examples for retrospective next-month DO regression |
| Proposed chronological splits | 02_training_candidate/train.csv, validation.csv, test.csv | 819 training, 176 validation and 435 test examples |
| Feature and target definitions | 02_training_candidate/feature_schema.json | Exact predictor list, target, metadata exclusions, split rules and timing limitations |
| Cleaned-data analysis | 03_analysis/EcoFlow_Cleaned_Data_Analysis.pdf | Four-page report with descriptive statistics, coverage, distributions, South Bay history, reporting patterns and training interpretation |
| Analysis tables and charts | 03_analysis | CSV results, machine-readable metrics, Markdown report and PNG charts |
| Secondary reference data | 04_reference_tables | Eleven normalized tables, 186 rows, profiles and original source cautions |
| Progress and review | 05_progress_and_review | Updated Week No. 2 document and source-reviewed workbook |
| Source materials | 06_sources | 56 original PDFs, source inventory, review images and download move manifest |
| Reproduction and R use | 07_scripts | R exploration/import scripts, Python analysis and preparation scripts, review transcriptions |
| Earlier unverified extraction | 08_unverified_extraction_archive | Preserved OCR ledger and review queues. Do not train on this folder. |

## Proposed model input and output

Input columns: station_id, do_t_mg_l, do_t_minus_1_mg_l, do_t_minus_2_mg_l, bod_t_mg_l, target_month_sin, target_month_cos.

Output column: target_do_next_month_mg_l, measured in mg/L. The origin month is t; the target month is t+1. Required months are explicitly calendar-adjacent. Use only the named predictors. Source record IDs, dates, split labels, example IDs and station_seen_in_training are metadata, not additional predictors.

No values were imputed and no model was trained. Censored or missing required values are excluded from the primary candidate. The separate alternative_do_history_only.csv has 1,558 examples and omits BOD, for a later coverage sensitivity comparison.

The proposed split is by target month: train through December 2022; validation in 2023; test from January 2024 to June 2026. All stations share date boundaries. Preprocessing must be fitted on training data only. Station XXIV has 12 examples in the test period and none in training; explicitly handle the unseen category and report its results separately. Full-period EDA has already been performed, so the proposed test period is not a blind research holdout.

## Findings and limits

Exact DO mean is 7.81 mg/L and median is 7.80 mg/L. Exact BOD mean is 2.57 mg/L and median is 2.00 mg/L. Available-cell summaries do not estimate a balanced lake-wide average. Three exact DO cells are below 5 mg/L; this is not a fish-kill label. Later reports use much coarser DO precision, which must be investigated before interpreting trends or model performance.

Actual sample days and publication timestamps are unavailable. A current-month value in a quarterly report may have become available after next month's target. The supplied supervised table is a proposed retrospective experiment until operational timing is established. It is not a fish-kill, carrying-capacity or gate-control training dataset, and does not replace the original thesis objectives.

## Running the scripts

The original project layout remains in the Research folder. From that folder in RStudio, source scripts/data_preparation/import_and_explore.R for exploration, or scripts/data_preparation/load_training_candidate.R to load the proposed splits and explicitly select predictors. R execution has not been verified because Rscript is unavailable in the inspected environment. Python EDA and source-link validation were executed.

The 07_scripts copies are provided for reference. The scripts use the existing Research project layout and dependencies; they are not standalone installers for this delivery folder. If using only this extracted package in R, change the base path to 01_cleaned_data or 02_training_candidate as appropriate. Python chart dependencies used for the executed analysis include pandas, numpy and matplotlib; PDF generation uses reportlab and pypdfium2.

The numbered folders are a snapshot of project deliverables. Original PDF filenames and data provenance are retained. Review image manifests retain their original project-relative paths; equivalent crops are in 06_sources/review_evidence. file_manifest.csv contains sizes and SHA256 hashes for the delivered files.
