cat("Installing Ch_2_Foundations_Demo.R dependencies...\n")

pkgs <- c("PCRA", "data.table", "xts", "PerformanceAnalytics",
          "PortfolioAnalytics", "foreach", "CVXR", "RPESE", "RPEIF",
          "ggplot2", "reshape2", "lubridate", "dplyr", "RobStatTM",
          "hitandrun", "devtools", "zoo", "lattice", "quadprog",
          "robustbase", "R.cache", "quantreg")

for (p in pkgs) {
  if (!requireNamespace(p, quietly = TRUE)) {
    cat("Installing:", p, "\n")
    install.packages(p, repos = "https://cran.r-project.org", quiet = TRUE)
  } else {
    cat("Already installed:", p, "\n")
  }
}

if (!requireNamespace("optimalRhoPsi", quietly = TRUE)) {
  cat("Installing optimalRhoPsi from GitHub...\n")
  devtools::install_github("kjellpk/optimalRhoPsi", quiet = TRUE)
} else {
  cat("Already installed: optimalRhoPsi\n")
}

cat("\nVerifying key packages...\n")
for (p in c("PCRA", "RobStatTM", "PortfolioAnalytics", "RPESE", "RPEIF", "optimalRhoPsi")) {
  tryCatch({
    library(p, character.only = TRUE)
    cat("OK:", p, "\n")
  }, error = function(e) {
    cat("FAIL:", p, "-", conditionMessage(e), "\n")
  })
}

cat("\nDone.\n")
cat("Session info:\n")
print(sessionInfo())
