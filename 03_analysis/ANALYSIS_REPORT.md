# Cleaned lake data analysis

Prepared 2 November 2026. Analysis uses exact source-reviewed lake BOD/DO only. No model was trained. Python was used for this analysis; R execution is still pending.

## Findings

- The release contains 3,384 exact values in 1,766 station-months from 52 quarterly reports. Across the reviewed cells, 24 are censored, 146 are source-missing, and one unreadable digit is excluded.
- Exact DO values have mean 7.81 mg/L and median 7.80 mg/L. Exact BOD has mean 2.57 mg/L and median 2.00 mg/L. These pooled summaries weight available cells and do not estimate a balanced lake-wide average.
- 3 reported DO cells are below 5 mg/L. This is a descriptive threshold count, not a fish-kill label. Monthly observations cannot reveal unobserved daily or hourly oxygen minima.
- Matched same-month BOD and DO have pooled Pearson r = 0.263 across 1,618 station-months. This is not a causal or out-of-sample predictive estimate. Station, time and reporting effects are not adjusted.
- Historical station coverage is longer than coverage at newly listed stations. The nine older station identities appear from 2013; six additional station identities appear in this reviewed series from 2021, and station XXIV from 2025. These are first appearances in the reviewed tables, not independently verified commissioning dates.
- Later reports contain many whole-number DO values. Annual changes may reflect measurement or reporting practice as well as environmental variation. Method and instrument metadata are needed before explaining this shift.
- Missingness has source-documented causes in some periods, including equipment failure, shallow water and weather. Complete-case training can therefore select a nonrepresentative subset; it is not justified to assume missingness is random.

## Candidate training file

training_do_next_month.csv has 1,430 complete supervised rows. Target: next-month DO in mg/L. Inputs: station ID, exact DO at t, t-1 and t-2, exact BOD at t, and the known target month as sine/cosine calendar features. Rows never jump across missing months. The DO-only alternative has 1,558 rows and can support a later coverage sensitivity comparison.

Proposed splits use target month, shared by all stations: train through December 2022, validation in 2023, and test from January 2024 through June 2026. Fit encoders and preprocessing on training data only. Earlier observations may be used across boundaries in a rolling forecast; future target labels may not be used as inputs. Full-period EDA has already been performed, so the proposed test period is not a blind research holdout.

Station XXIV appears only in the proposed test period. Its 12 test examples require explicit handling of an unseen categorical station ID. Fit encoders on training data and report new-station performance separately from performance at known stations.

Current-month BOD/DO from a quarterly publication may not have been available before next month's target. Publication and actual sample timestamps are unknown. This candidate supports a retrospective observational experiment until timely operational input availability is established. It does not supply fish-kill, capacity or gate-control labels.

## Files

Descriptive CSVs and charts are in this analysis folder. Reviewed source data are under data/analysis_ready/llda_lake_bod_do_v1. Candidate training tables and feature_schema.json are under data/training_candidates/do_next_month_v1. Source locators, missing categories and correction logs are preserved in the reviewed release.
