# Open the Research folder in RStudio before sourcing. No model is trained.
base <- file.path(getwd(), "data", "training_candidates", "do_next_month_v1")
load_split <- function(name) read.csv(file.path(base, paste0(name, ".csv")), fileEncoding="UTF-8-BOM", stringsAsFactors=FALSE)
train <- load_split("train")
validation <- load_split("validation")
test <- load_split("test")
features <- c("station_id", "do_t_mg_l", "do_t_minus_1_mg_l", "do_t_minus_2_mg_l", "bod_t_mg_l", "target_month_sin", "target_month_cos")
target <- "target_do_next_month_mg_l"
X_train <- train[features]
y_train <- train[[target]]
X_validation <- validation[features]
y_validation <- validation[[target]]
X_test <- test[features]
y_test <- test[[target]]
stopifnot(nrow(train)==819, nrow(validation)==176, nrow(test)==435)
stopifnot(!anyNA(X_train), !anyNA(y_train), !anyNA(X_validation), !anyNA(y_validation), !anyNA(X_test), !anyNA(y_test))
stopifnot(max(train$target_month)<min(validation$target_month), max(validation$target_month)<min(test$target_month))
print(data.frame(split=c("train","validation","test"), rows=c(nrow(train),nrow(validation),nrow(test))))
print(setdiff(unique(test$station_id), unique(train$station_id)))
# station_id remains character. Fit a categorical encoder on train only and
# handle unseen station XXIV explicitly before fitting your selected estimator.
# Never select all remaining columns automatically: source IDs and metadata
# must not enter X. Read feature_schema.json for timing and evaluation limits.
