# Run from the Research project folder in RStudio. Base R only.
# This script imports and explores the reviewed release; it trains no model.
args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args)) normalizePath(args[1], mustWork = TRUE) else getwd()
base <- file.path(root, "data", "analysis_ready", "llda_lake_bod_do_v1")
if (!file.exists(file.path(base, "lake_numeric_analysis.csv"))) stop("Run from Research or pass its path to Rscript")
read_clean <- function(name) read.csv(file.path(base, name), fileEncoding = "UTF-8-BOM", na.strings = "", stringsAsFactors = FALSE, check.names = FALSE)
numeric_data <- read_clean("lake_numeric_analysis.csv")
reviewed <- read_clean("lake_measurements_reviewed_long.csv")
panel <- read_clean("lake_station_month_calendar.csv")
coverage <- read_clean("station_parameter_coverage.csv")
numeric_data$numeric_value <- as.numeric(numeric_data$numeric_value)
stopifnot(nrow(numeric_data) == 3384L, nrow(reviewed) == 3555L)
stopifnot(!anyDuplicated(numeric_data[c("station_id", "observation_month", "parameter")]))
stopifnot(all(numeric_data$qualifier == "="), all(!is.na(numeric_data$numeric_value)))
output <- file.path(root, "outputs", "analysis_release", "r_exploration")
dir.create(output, recursive = TRUE, showWarnings = FALSE)
write.csv(aggregate(numeric_value ~ parameter, numeric_data, function(x) c(n=length(x), mean=mean(x), sd=sd(x), min=min(x), max=max(x))), file.path(output, "descriptive_statistics.csv"), row.names=FALSE)
write.csv(as.data.frame(table(reviewed$parameter, reviewed$value_status)), file.path(output, "missing_and_censored_counts.csv"), row.names=FALSE)
write.csv(coverage, file.path(output, "coverage.csv"), row.names=FALSE)
png(file.path(output, "south_bay_do.png"), width=1200, height=650)
south <- panel[panel$station_id == "L_VIII", ]
# First-of-month dates are plotting anchors, not actual sample dates.
plot(as.Date(paste0(south$observation_month, "-01")), south$dissolved_oxygen_mg_l,
     type="l", xlab="Reported observation month", ylab="Dissolved oxygen (mg/L)", main="South Bay reported monthly dissolved oxygen")
dev.off()
capture.output(sessionInfo(), file=file.path(output, "session_info.txt"))
message("Imported reviewed data and saved exploration outputs. No model trained.")
