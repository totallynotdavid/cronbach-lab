# Cross-check Python's alpha against psych::alpha.
#
#   Rscript r/crosscheck.R results/datasets     compare every dataset to python_alpha.csv
#   Rscript r/crosscheck.R some_items.csv       just print psych's alpha for one dataset
#
# Exits with status 1 if any value differs from Python by more than 1e-6.

suppressPackageStartupMessages(library(psych))

tolerance <- 1e-6
args <- commandArgs(trailingOnly = TRUE)
target <- if (length(args) >= 1) args[1] else "results/datasets"

# check.keys = FALSE: do not flip items that correlate negatively. Python does
# not either, and psych would otherwise change the scale being compared.
psych_alpha <- function(path) {
  # psych prints its reversed-item advice with cat(), hence capture.output.
  invisible(capture.output(fit <- suppressWarnings(suppressMessages(
    psych::alpha(read.csv(path), check.keys = FALSE)
  ))))
  c(raw = fit$total$raw_alpha, std = fit$total$std.alpha)
}

if (!dir.exists(target)) {
  a <- psych_alpha(target)
  cat(sprintf("raw alpha %.10f\nstd alpha %.10f\n", a["raw"], a["std"]))
  quit(status = 0)
}

python <- read.csv(file.path(target, "python_alpha.csv"))
result <- do.call(rbind, lapply(seq_len(nrow(python)), function(i) {
  a <- psych_alpha(file.path(target, paste0(python$dataset[i], ".csv")))
  data.frame(
    dataset = python$dataset[i],
    r_raw = a["raw"], py_raw = python$raw_alpha[i],
    r_std = a["std"], py_std = python$std_alpha[i]
  )
}))
result$max_diff <- pmax(abs(result$r_raw - result$py_raw), abs(result$r_std - result$py_std))
result$agree <- result$max_diff <= tolerance

options(width = 200, digits = 10)
print(result, row.names = FALSE)
if (all(result$agree)) {
  cat(sprintf("\nOK: %d datasets agree within %g\n", nrow(result), tolerance))
} else {
  cat(sprintf("\nFAIL: %d of %d datasets differ by more than %g\n",
              sum(!result$agree), nrow(result), tolerance))
  quit(status = 1)
}
