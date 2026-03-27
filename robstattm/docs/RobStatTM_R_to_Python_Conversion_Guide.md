# RobStatTM R → Python Conversion Guide

This guide is based on the **RobStatTM** [CRAN documentation](https://cran.r-project.org/web/packages/RobStatTM/RobStatTM.pdf) and the [statsmodels](https://www.statsmodels.org/) robust and regression APIs. It shows how to reproduce the book examples (e.g. flour, shock) in Python and how to map core R functions to Python.

---

## 1. Documentation and references

| Source | What it covers |
|--------|-----------------|
| **CRAN RobStatTM.pdf** | Full reference: `locScaleM`, `lmrobM`, `lmrobM.control`, `lmrobdet.control`, `scaleM`, `bisquare`, `huber`, `rob.linear.test`, datasets, etc. |
| **statsmodels Robust Linear Models** | [RLM](https://www.statsmodels.org/stable/robust_linear_model.html): M-estimation for regression (Huber, TukeyBiweight, etc.) via IRLS. |
| **statsmodels Robust norms** | [TukeyBiweight](https://www.statsmodels.org/stable/generated/statsmodels.robust.norms.TukeyBiweight.html) (bisquare), [HuberT](https://www.statsmodels.org/stable/generated/statsmodels.robust.norms.HuberT.html), scale options. |
| **statsmodels QuantReg** | [QuantReg](https://www.statsmodels.org/dev/generated/statsmodels.regression.quantile_regression.QuantReg.html): quantile regression; τ=0.5 gives L1 (median) regression. |

---

## 2. R → Python function mapping

### 2.1 Regression

| R (RobStatTM / stats) | Python | Notes |
|------------------------|--------|--------|
| `lm(y ~ x, data)` | `sm.OLS(y, sm.add_constant(X)).fit()` | Least squares. |
| `quantreg::rq(y ~ x, data)` | `sm.QuantReg(y, sm.add_constant(X)).fit(q=0.5)` | L1 (median) regression. |
| `lmrobM(y ~ x, data, control=...)` | `sm.RLM(y, X, M=sm.robust.norms.TukeyBiweight(c=...)).fit(scale_est='mad', ...)` | M-estimate with bisquare; tune `c` for target efficiency (see below). |
| `lmrobdet.control(bb=0.5, efficiency=0.85, family="bisquare")` | Use `TukeyBiweight(c=...)`; for 85% efficiency the tuning constant differs from default 4.685 (95%). | Match efficiency via tuning constant if needed. |

**RLM (M-estimation) in Python:**

- **Norms:** `HuberT()`, `TukeyBiweight(c=4.685)` (bisquare; default c ≈ 95% eff), `Hampel()`, `AndrewWave()`, `RamsayE()`, `TrimmedMean()`, `LeastSquares()`.
- **Scale:** `scale_est='mad'` (MAD) or `'HuberScale'`.
- **Convergence:** `maxiter`, `tol` in `RLM.fit()`.

**Tuning constant for efficiency:**  
RobStatTM uses `bisquare(e)` to get the constant for efficiency `e` (e.g. 0.85). In statsmodels, `TukeyBiweight(c=4.685)` is the default (≈95% efficiency). For 85% efficiency you need a smaller `c` (e.g. around 4.0–4.2 depending on implementation); check statsmodels docs or match R’s `bisquare(0.85)` numerically.

### 2.2 Location and scale (univariate)

| R (RobStatTM) | Python | Notes |
|----------------|--------|--------|
| `locScaleM(x, psi="bisquare", eff=0.95)` | No direct built-in. Implement IRLS: initial scale = MAD, then location M-step with bisquare/Huber. | Returns `mu`, `std.mu`, `disper`. See `flour_example.py` for a minimal implementation. |
| `scaleM(x, ...)` | MAD: `np.median(np.abs(x - np.median(x)))`; or scale from RLM if in regression. | M-scale needs iterative solution; MAD is a robust starting value. |
| `mean(x)`, `sd(x)` | `np.mean(x)`, `np.std(x, ddof=1)` | Classical. |

### 2.3 Robust tests

| R | Python | Notes |
|---|--------|--------|
| `rob.linear.test(full, reduced)` | No direct equivalent. Implement Wald-type test using (β_full − β_reduced), robust cov matrix, and χ²/F. | See book Section 4.7.2; requires covariance of M-estimator. |

### 2.4 Data

- **In R:** `data(shock)`, `data(flour)` after `library(RobStatTM)`.
- **In Python:** Export from R to CSV and load with pandas, or use the small inline datasets in the example scripts. Example in R:
  ```r
  library(RobStatTM)
  write.csv(shock, "shock.csv", row.names = FALSE)
  write.csv(flour, "flour.csv", row.names = FALSE)
  ```

---

## 3. Implementation details (from the documentation)

### locScaleM (RobStatTM)

- **Purpose:** M-estimators for location and scale (univariate).
- **Signature:** `locScaleM(x, psi = "mopt", eff = 0.95, maxit = 50, tol = 1e-04, na.rm = FALSE)`.
- **Returns:** `mu` (location), `std.mu` (SE of location), `disper` (M-scale).
- **Psi:** `"bisquare"`, `"huber"`, `"opt"`, `"mopt"`. Efficiency options (e.g. 0.85, 0.9, 0.95) set the tuning constant.

### lmrobM (RobStatTM)

- **Purpose:** Robust regression for linear models (fixed design). Uses L1 as initial estimate, then redescending M-estimator with scale from a quantile of absolute L1 residuals.
- **Control:** `lmrobM.control(bb = 0.5, efficiency = 0.85, family = "bisquare", max.it = 100, rel.tol = 1e-07, ...)`.
- **Returns:** `coefficients`, `scale`, `residuals`, `converged`, `iter`, `rweights`, `fitted.values`, `cov`, etc.

### statsmodels RLM

- Fits by IRLS; scale can be MAD or Huber.
- Use `TukeyBiweight(c=...)` for bisquare; adjust `c` to approximate RobStatTM efficiency if needed.

---

## 4. Step-by-step conversion workflow

1. **Identify R calls** in the script (e.g. `locScaleM`, `lm`, `rq`, `lmrobM`, `plot`, `abline`).
2. **Map to Python** using the table above (and statsmodels/scipy/numpy).
3. **Get data** into Python (CSV from R or inline).
4. **Match options** where possible (e.g. efficiency → tuning constant for TukeyBiweight).
5. **Reproduce outputs** (tables, plots) and compare to R/book.

---

## 5. Example scripts in this project

- **`robstattm/python/flour_example.py`** – Replicates flour.R: mean, M-estimate of location (custom `locScaleM`-like), 25% trimmed mean, SEs, 0.95 CIs (Table 2.4).
- **`robstattm/python/shock_example.py`** – Replicates shock.R: LS, LS without outliers, L1 (QuantReg), M-estimate (RLM with TukeyBiweight), and scatter plots (Figures 4.1 & 4.3).

Run from project root (with dependencies installed):

```bash
pip install numpy pandas matplotlib statsmodels scipy
python robstattm/python/flour_example.py
python robstattm/python/shock_example.py
```

---

## 6. Limitations and differences

- **locScaleM:** Python has no built-in; the flour example uses a simple IRLS location+scale with MAD start and a bisquare-like weight. For exact parity use the same ψ and efficiency as in R.
- **Tuning constants:** R’s `bisquare(0.85)` vs statsmodels’ default TukeyBiweight may give slightly different coefficients; adjust `c` if you need to match R.
- **rob.linear.test:** Not in statsmodels; implement from the book’s formula if you need robust ANOVA/F-tests in Python.

Using this guide and the two example scripts, you can convert other RobStatTM scripts (e.g. oats, mineral) by applying the same mappings and adding data loading and plots as needed.
