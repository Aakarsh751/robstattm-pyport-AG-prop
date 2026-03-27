# =============================================================================
# RobStatTM Setup and Example Script
# Run this in R or RStudio after installing R.
# Purpose: Install RobStatTM + required packages, then run flour, shock, oats.
# =============================================================================

# -----------------------------------------------------------------------------
# STEP 1: Install packages (uncomment and run once)
# -----------------------------------------------------------------------------
# Install RobStatTM from CRAN (also installs pyinit, rrcov, robustbase)
install.packages("RobStatTM", dependencies = TRUE)

# Extra package needed for shock.R (Example 4.1) and mineral.R
install.packages("quantreg")

# Optional: for other scripts later (see RobStatTM_Study_and_Setup_Guide.md)
# install.packages("robustbase")  # wood.R data
# install.packages("robust")      # leukemia.R, epilepsy.R
# install.packages("robustarima") # Ch 8 time series

# -----------------------------------------------------------------------------
# STEP 2: Verify installation
# -----------------------------------------------------------------------------
cat("Loading RobStatTM...\n")
library(RobStatTM)
data(shock)
cat("RobStatTM loaded. Shock data (first 2 rows):\n")
print(head(shock, 2))
cat("\nScripts folder in installed package:\n")
print(system.file("scripts", package = "RobStatTM"))

# -----------------------------------------------------------------------------
# STEP 3: Set working directory to project root
# -----------------------------------------------------------------------------
# Change this path if your project is elsewhere
project_root <- "C:/ProfDM_Rproject"
if (dir.exists(project_root)) {
  setwd(project_root)
  cat("\nWorking directory set to:", getwd(), "\n")
} else {
  cat("\nFolder not found:", project_root, "\n")
  cat("Please set working directory manually to the ProfDM_Rproject folder.\n")
}

# -----------------------------------------------------------------------------
# STEP 4: Run example scripts from robstattm/examples-scripts
# -----------------------------------------------------------------------------
scripts_dir <- file.path("robstattm", "examples-scripts")
if (!dir.exists(scripts_dir)) {
  cat("Folder", scripts_dir, "not found. Skipping script runs.\n")
} else {

  # 4a. flour.R (Example 1.1, Table 2.4) - no extra package
  cat("\n--- Running flour.R (Example 1.1, Table 2.4) ---\n")
  tryCatch(
    source(file.path(scripts_dir, "flour.R")),
    error = function(e) cat("Error:", conditionMessage(e), "\n")
  )

  # 4b. shock.R (Example 4.1, Figures 4.1 & 4.3) - needs quantreg
  cat("\n--- Running shock.R (Example 4.1) ---\n")
  if (!requireNamespace("quantreg", quietly = TRUE)) {
    cat("Install quantreg first: install.packages(\"quantreg\")\n")
  } else {
    tryCatch(
      source(file.path(scripts_dir, "shock.R")),
      error = function(e) cat("Error:", conditionMessage(e), "\n")
    )
  }

  # 4c. oats.R (Example 4.2, Figures 4.2 & 4.4)
  cat("\n--- Running oats.R (Example 4.2) ---\n")
  tryCatch(
    source(file.path(scripts_dir, "oats.R")),
    error = function(e) cat("Error:", conditionMessage(e), "\n")
  )
}

cat("\nDone. See robstattm/docs/RobStatTM_Study_and_Setup_Guide.md for full instructions.\n")
cat("Session info:\n")
print(sessionInfo())
