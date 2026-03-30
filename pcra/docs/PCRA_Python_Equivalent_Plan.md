# How to Create a Python Equivalent of the PCRA Package

**Plan Document**  
Based on: GitHub (robustport/PCRA), CRAN Manual (55 pages), four vignettes, and Ch_2_Foundations_Demo.R

---

## 1. Understanding What PCRA Actually Is

From studying the GitHub source (robustport/PCRA), the CRAN manual (55 pages), all four vignettes, and the full Ch_2_Foundations_Demo.R, **PCRA has three distinct layers**:

---

### Layer A: Data  
*(The most valuable and hardest to replicate)*

| Dataset | Description |
|--------|-------------|
| **stocksCRSPmonthly** | 81,144 rows × 14 columns: monthly returns for 294 CRSP stocks (1993–2015) |
| **stocksCRSPweekly** / **stocksCRSPdaily** | Same stocks at higher frequencies |
| **factorsSPGMI** / **factorsSPGMIr** | 81,144 rows × 22 columns: 14 SPGMI alpha factors for those 294 stocks |
| **SP500**, **SP500from1967to2007**, **SPIndustrials**, **SP400Industrials**, **SP425Industrials** | Historical S&P index data |
| **FRBinterestRates** | 90-day bill rates (1934–2014) |
| **edhec** (from PerformanceAnalytics) | Hedge fund strategy returns |
| ~15 individual stock return datasets | retDD, retEDS, retFNB, retKBH, retMER, retOFG, retPSC, retVHI, retWTS, etc. |
| **CboeOptionStrategies**, **ConferenceBoardETI**, **ShortDurationCredit**, **USTreasuryTradeweb** | Options, employment, credit, Treasury data |

---

### Layer B: Functions  
*(~40 exported functions in the R/ folder)*

| Category | Count | Examples |
|----------|-------|----------|
| Efficient frontier math | 7 | mathEfrontRiskyMuCov, mathGmv, mathTport, mathWtsEfrontRiskyMuCov |
| Data selection/manipulation | 5 | selectCRSPandSPGMI, stocksCRSPxts, returnsCRSPxts, getPCRAData, to_monthly/to_weekly |
| Portfolio analytics | 6 | barplotWts, bootEfronts, chart.Efront, opt.outputMvoPCRA, minVarCashRisky, minVarRiskyLO |
| Visualization | 5 | tsPlotMP, barplotWts, ellipsesPlotPCRA.covfm |
| Robust statistics integration | 4 | plotLSandRobustSFM, plotLSandHuberRobustSFM, cleanOutliers, meanReturns4Types |
| Statistical utilities | 6+ | divHHI, levgLongShort, turnOver, winsorize, winsorMean, KRest, SKest, psiHuber, qqnormDatWindat, ewmaMeanVol, transferCoef |

---

### Layer C: Ecosystem Glue  

PCRA **orchestrates 12+ other R packages**. The demo scripts call into:

- **PortfolioAnalytics** — portfolio spec, constraints, objectives, rebalancing
- **PerformanceAnalytics** — Return.rebalancing, Drawdowns, table.Drawdowns
- **RPESE** / **RPEIF** — influence-function standard errors for risk measures
- **RobStatTM** — locScaleM, scaleM, lmrobdetMM
- **optimalRhoPsi** — rho_modOpt, psi_modOpt, computeTuningPsi_modOpt
- **CVXR** — convex optimization solver
- **ggplot2**, **lattice**, **xts**, **zoo**, **data.table**, **quadprog**, **corpcor**, **boot**, **robustbase**

---

## 2. Python Package Structure

```
pcra/
├── __init__.py
├── data/
│   ├── __init__.py
│   ├── loader.py
│   └── csv/
├── frontier/
│   ├── __init__.py
│   ├── math_efront.py
│   ├── gmv.py
│   └── weights.py
├── optimization/
│   ├── __init__.py
│   ├── rebalancing.py
│   └── constraints.py
├── risk/
│   ├── __init__.py
│   ├── measures.py
│   ├── ratios.py
│   ├── drawdowns.py
│   ├── influence_functions.py
│   └── leverage.py
├── robust/
│   ├── __init__.py
│   ├── location_scale.py
│   ├── psi_functions.py
│   ├── regression.py
│   └── covariance.py
├── selection/
│   ├── __init__.py
│   └── select.py
├── visualization/
│   ├── __init__.py
│   ├── ts_plot.py
│   ├── barplot_wts.py
│   └── efront_plot.py
└── utils/
    ├── __init__.py
    ├── statistics.py
    └── returns.py
```

---

## 3. Function-by-Function Mapping: R → Python

### Efficient Frontier (pure math)

| R Function | Python approach | Library |
|------------|-----------------|---------|
| mathEfrontRiskyMuCov | Merton closed-form σ(μ) | numpy |
| mathEfrontRisky | Same, μ and V from returns | numpy |
| mathEfrontCashRisky | Tangent line from rf to tangency | numpy |
| mathEfront | Risky frontier + cash-risky line | numpy |
| mathGmv / mathGmvMuCov | w = V⁻¹·1 / (1ᵀV⁻¹·1) | numpy |
| mathTport | w = V⁻¹·(μ − rf·1) / sum(...) | numpy |
| mathWtsEfrontRisky / mathWtsEfrontRiskyMuCov | w(μₑ) = z₁(b−aμₑ)/d + z₂(cμₑ−a)/d | numpy |

### Portfolio Optimization

| R | Python | Library |
|---|--------|---------|
| portfolio.spec, add.constraint, add.objective | Dict/class + cp.sum(w)==1, w>=0, cp.Minimize(cp.quad_form(w,V)) | cvxpy |
| optimize.portfolio.rebalancing(rolling_window=60) | Loop: trailing 60-month window, solve QP, store weights | cvxpy + pandas |
| Return.rebalancing(returns, weights) | (returns * weights.shift(1)).sum(axis=1) | pandas |

### Risk & Performance

| R | Python | Library |
|---|--------|---------|
| sd, SemiDeviation, VaR, ES, Sharpe, Sortino | std, downside_std, percentile, mean of tail | numpy |
| Drawdowns, table.Drawdowns | cum/cummax − 1; scan for peaks/troughs | pandas |
| RPESE SD.SE, ES.SE, VaR.SE, SR.SE (IFiid) | IF-based SE formulas | scipy + custom |
| divHHI, turnOver, levgLongShort | 1−sum(w²), sum(abs(diff(w))) | numpy, pandas |

### Robust Statistics

| R | Python | Library |
|---|--------|---------|
| locScaleM | IRLS with bisquare/mOpt ψ | scipy + custom |
| scaleM(family="mopt") | M-scale Newton-Raphson | custom |
| optimalRhoPsi rho_modOpt, psi_modOpt | Polynomial ρ/ψ | numpy |
| computeTuningPsi_modOpt(eff) | Root-find cc for target efficiency | scipy.integrate + optimize |
| plotLSandRobustSFM | OLS + RLM, outlier weights | statsmodels + matplotlib |
| cleanOutliers, winsorize, winsorMean | med±k·mad clip; percentile clip | numpy |

### Data Selection & Viz

| R | Python | Library |
|---|--------|---------|
| selectCRSPandSPGMI | Filter by date/columns, pivot to wide | pandas |
| stocksCRSPxts, returnsCRSPxts | Pivot index=Date, columns=TickerLast | pandas |
| getPCRAData | Load CSV or download from GitHub | pandas, requests |
| tsPlotMP, barplotWts, chart.Efront | subplots, bar chart, frontier plot | matplotlib |

---

## 4. Python Dependencies

| Purpose | Package |
|---------|---------|
| Core computation | numpy |
| Data handling | pandas |
| Optimization | cvxpy |
| Robust / stats | scipy |
| Robust regression | statsmodels |
| Plotting | matplotlib |
| R data extraction (one-time) | pyreadr |

---

## 5. Phased Roadmap

| Phase | Scope | Effort |
|-------|--------|--------|
| **1. Core math** | All mathEfront*, mathGmv*, mathTport, mathWtsEfront* | 2–3 weeks |
| **2. Data layer** | Extract datasets to CSV; load_*(); selectCRSPandSPGMI equivalent | 1 week |
| **3. Risk measures** | SD, SemiSD, VaR, ES, ratios, drawdowns, turnover, divHHI; IF standard errors | 2 weeks |
| **4. Optimization + rebalancing** | cvxpy constraints/objectives; rolling-window rebalancing loop | 2–3 weeks |
| **5. Robust statistics** | locScaleM, M-scale, mOpt ψ, tuning constant, robust SFM | 3–4 weeks |
| **6. Visualization** | tsPlotMP, barplotWts, frontier plots | 1 week |

---

## 6. Gaps: No Direct Python Equivalent

1. **RPESE/RPEIF** — Influence-function SEs for risk measures; implement from theory.
2. **optimalRhoPsi** — mOpt ψ and efficiency-based tuning; implement from formulas.
3. **PortfolioAnalytics rebalancing** — Full rolling-window backtest framework; build with cvxpy + pandas.

---

## 7. Connection to GSoC 2026: RobStatTM Python Package

The PCRA replication represents a **natural Phase 2 extension** of the core GSoC 2026
deliverable — a Python equivalent of the **RobStatTM** R package (robust statistics for
portfolio risk analysis).

### Why PCRA comes after RobStatTM

PCRA depends directly on RobStatTM for three of its most important capabilities:

| PCRA usage | RobStatTM function | Chapter 2 demo |
|---|---|---|
| Robust location estimate with SE | `locScaleM` | Figure 2.38, Table 2.7 |
| Robust scale (M-estimator, mOpt) | `scaleM(family="mopt")` | Table 2.8 |
| Robust regression | `lmrobdetMM` | Used in SFM robust plots |

A working Python **RobStatTM-Py** package (the GSoC deliverable; `pip install robstatm-py`) is a hard prerequisite
for the PCRA Python equivalent. Once the robust statistics layer exists natively in
Python, the PCRA functions listed in Section 2–3 above can be built on top of it.

### Phased dependency diagram

```
GSoC 2026 Core (RobStatTM-Py)
  ├── locScaleM, scaleM, lmrobdetMM, covRobMM, covRobRocke, pcaRobS
  └── Validated against R ground truth via rpy2 test oracle
          │
          ▼
Post-GSoC Extension (pcrapy)
  ├── frontier/    — mathEfront*, mathGmv, mathTport  (pure NumPy, already done)
  ├── risk/        — SD/ES/VaR with IF standard errors (RPESE/RPEIF reimplementation)
  ├── optimization/— rolling GmvLS via cvxpy  (already demonstrated)
  ├── robust/      — delegates to RobStatTMPY
  ├── data/        — CRSP/SPGMI dataset access layer
  └── visualization— tsPlotMP, barplotWts, chart.Efront
```

### Proof-of-concept already completed

The `pcra/python/ch2_foundations_demo.py` script in this repository is the working
proof-of-concept. It reproduces **16 figures** (2.1–2.38) from Chapter 2 in pure Python,
side-by-side with the original R output, with 100% visual parity on all mathematical
figures and close numerical agreement on the data-driven figures.

The side-by-side comparison is available as a single organized PDF:
**`pcra/output/Ch2_Comparison.pdf`** (generated by `pcra/tools/make_comparison_pdf.py`).

### What this demonstrates for the GSoC proposal

1. **Feasibility**: Full PCRA chapter reproduction is achievable in pure Python with
   NumPy, SciPy, pandas, matplotlib, and cvxpy — no R required at runtime.
2. **Scope clarity**: The robust statistics core (RobStatTM-Py) is a well-defined,
   self-contained first deliverable. PCRA adds a portfolio analytics layer on top.
3. **Presentation material**: The Ch2_Comparison.pdf can be shown directly as evidence
   of progress in GSoC midterm/final evaluations and in the proposal itself.

---

*Document generated for the PCRA-to-Python conversion project.*
