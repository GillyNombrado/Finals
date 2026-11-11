# EcoFlow Optima analysis release

Prepared 2 November 2026. Cleaning is complete for the defined lake BOD and dissolved oxygen release. The broader water quality archive is retained separately and is not fully source-validated.

## Verified scope and counts

We reviewed the lake BOD/DO table in all 52 available quarterly reports, covering January 2013 to June 2026 with gaps. The 56-PDF collection also contains four annual or special reports outside this release. The reviewed release has 3,555 parameter cells: 3,384 exact numeric values, 24 censored values, 146 source-missing values and 1 unreadable digit excluded from numeric analysis. These are parameter cells, not independent samples. There are 1,766 station-months containing at least one exact value across 16 station identities.

The complete calendar has 2,592 station-month rows, including periods when stations were not listed. Do not interpret the calendar row count as sampled observations. Station expansion is represented explicitly rather than backfilling newer stations.

## What to use

- lake_numeric_analysis.csv contains exact source-reviewed numeric values in long form.
- lake_measurements_reviewed_long.csv retains all reviewed values and their meanings.
- lake_station_month_calendar.csv is the calendar-aligned wide input for R and later feature engineering. Missing measurements remain blank, with separate status and censoring fields.
- station_parameter_coverage.csv gives exact-value counts and genuine consecutive-month coverage.
- source_review_audit.csv and source_review_corrections.csv trace the review to original PDF pages, station rows and month columns.
- non_exact_values.csv isolates source gaps, censoring and the unreadable digit. The unreadable digit is the January 2018 DO value for Sta. Rosa and must not be guessed.
- prior_extraction_dispositions.csv accounts for every earlier extraction record. Earlier lake cells covered here are superseded. Other parameters and tributaries are excluded from this analysis release, with their raw extraction preserved.
- The 11 normalized compiled reference tables are under ../compiled_reference_v1. All 186 rows were retained and profiled. They remain secondary references, with their original cautions.

## Cleaning rules and source findings

Only exact values enter numeric analysis. A reported <1 remains a bound, not 0, 0.5 or 1. Blank cells, gray no-data cells and printed missing symbols are distinguished. Missing analysis was sometimes documented in the source, including the September 2021 incubator breakdown, strong winds at station XVII in August 2021, shallow-water sites in April 2024, and Typhoon Ulysses in November 2020. None of these gaps is imputed.

The 2014 Q1 appended April-June tables remain excluded because their period conflicts with the report. No 2014 Q3 or 2020 Q2 observations were invented. BOD columns are absent from the reviewed lake table in 2014 Q4 and 2015 Q1/Q2; this is recorded as a scope exclusion rather than an agency missing sample. Total/fecal coliform and nutrient distinctions remain in the broader archive and are not silently merged here.

Original PDFs are unchanged. Downloads were organized through hash matching and explicit project archive names. All 67 moved items have a manifest, and moved file hashes were verified. Unrelated Downloads files were left in place.

## Feasibility before training

There are 1,696 candidate station-level pairs with an exact DO value in month t and t+1. The South Bay station has 152 exact DO observations and a longest continuous run of 66 months. These counts demonstrate data availability for a retrospective monthly forecasting experiment, not independence of station observations or operational early-warning ability.

The source reports show a change from decimal DO values to many whole-number reported values in later periods. Preserve the published precision and investigate this reporting shift in EDA and holdout performance. Do not manufacture decimal precision or treat reporting changes as environmental trends. Exact station coordinates/relocations and historical measurement methods are not established.

The current data does not provide a complete fish-kill event register with reliable negative examples, sustainable stocking-capacity outcomes, or actual gate operation logs. The original platform objectives remain unchanged. A monthly water-quality model would be a supporting component whose role needs an explicit research decision.

Actual sampling days and publication/availability timestamps are unknown. A quarterly report containing a monthly value does not prove that value was available in real time during that month. Prospective claims require an operational input source and a documented timing policy. Otherwise describe the experiment as retrospective.

## Next steps before training

1. Explore distributions, missingness and station histories. Reviewed CSVs and coverage report available; run the R exploration script and inspect plots.

2. Define thesis output and monthly prediction horizon. Written target, unit, population and horizon; agree how this supports the original platform objectives.

3. Establish what inputs exist at prediction time. Sampling/publication timing and deployment data source documented; retrospective use stated if timing cannot be recovered.

4. Prepare lags and chronological validation. Lag windows do not cross missing calendar months; same calendar holdout for all stations; transformations fit on training data only.

5. Check reporting changes and remaining source uncertainty. Sensitivity to rounded DO values, station expansion, censored BOD and one excluded digit recorded; optional independent transcription review.

6. Train and compare baseline models. Persistence and seasonal baselines compared with simple regression and a tree model; MAE/RMSE and station/year breakdowns reported.


The prepared R script is scripts/data_preparation/import_and_explore.R. It uses base R and does not install packages. Rscript was not available in the inspected environment, so R execution remains pending. Python release checks passed, including source integrity, unique keys, missing/censored exclusion, calendar continuity and count reconciliation. No model has been trained.

Source collection: https://llda.gov.ph/ldb-and-its-tributaries/
