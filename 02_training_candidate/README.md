# Next month DO training candidate

Use training_do_next_month.csv as the combined candidate table, or train.csv, validation.csv and test.csv for the proposed chronological split. Read feature_schema.json first: it lists predictor columns, the target and metadata that must not enter the model.

The target is next-month dissolved oxygen in mg/L. Inputs are station identity, exact DO in the current and preceding two months, exact current-month BOD, and the known target month as cyclic calendar features. Every required month is checked against the calendar. Rows with missing or censored required values are excluded without imputation. alternative_do_history_only.csv is a separate candidate for studying whether requiring BOD unnecessarily reduces coverage.

This is a proposed retrospective forecasting dataset. Report publication times are unknown, so timely operational availability of current-month inputs has not been established. It is not a fish-kill classification, carrying-capacity or gate-control training dataset. No model has been trained. Full-period descriptive exploration has been performed; the future test split is not a blind, previously unseen research holdout.
