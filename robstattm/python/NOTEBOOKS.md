# RobStatTM comparison notebooks

## `robstatpy_comparison_rpy2.ipynb` (primary)

Calls **RobStatTM** from Python using **rpy2**. This is the main demonstration for the GSoC proposal.

- **Part I — rpy2 bridge:** `locScaleM`, `scaleM`, `lmrobdetMM`, `covRobMM` / `covRobRocke`, `pcaRobS`.  
  Uses `importr("RobStatTM")`, `R('...')` for R code, `.rx2()` / `r2py()` to pull results into NumPy.  
  `set_conversion(default_converter)` is set so conversions behave under Jupyter.
- **Appendix A — optional:** pure-Python univariate cross-checks for `locScaleM` / `scaleM` only (not the primary deliverable).

Output figures live under [`figures/`](figures/).

## `robstatpy_comparison.ipynb` (alternate)

Uses a **subprocess** + **jsonlite** path to R instead of rpy2. Kept for comparison; the proposal focuses on the rpy2 notebook above.
