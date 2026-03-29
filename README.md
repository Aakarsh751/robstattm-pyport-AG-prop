# robstattm-pyport-AG

**Companion repository for the GSoC 2026 proposal: Python Wrappers for RobStatTM**
Aakarsh Gupta · University of Washington · April 2026

---

## What this repo is

This repository was built to **support and demonstrate** the GSoC 2026 project proposal
[`docs/gsoc2026_proposal/proposal_v4.pdf`](docs/gsoc2026_proposal/proposal_v4.pdf).

The proposal describes building **`robstatpy`** — a Python library that wraps the
[RobStatTM](https://cran.r-project.org/package=RobStatTM) R package, making its
robust statistical estimators (MM-regression, robust covariance, robust PCA, and more)
available to Python users with no R knowledge required.

Everything in this repo is working, runnable code produced **before the GSoC period starts**,
to demonstrate readiness for the project.

### How the rpy2 “bridge” is built here (important)

| What | Where |
|------|--------|
| **Notebook driver** | [`robstattm/python/robstatpy_comparison_rpy2.ipynb`](robstattm/python/robstatpy_comparison_rpy2.ipynb) — loads `rpy2`, `importr("RobStatTM")`, sets `set_conversion(default_converter)` for Jupyter, defines helpers `R()`, `rx()`, `r2py()`. |
| **Generator (source of truth for cells)** | [`robstattm/python/build_notebook_rpy2.py`](robstattm/python/build_notebook_rpy2.py) — rebuilds the notebook with `python build_notebook_rpy2.py`. |
| **Thin `robstattm.*` API calls** | **Not used in the notebook.** After `robstattm = importr("RobStatTM")`, the notebook still calls R via **`R('...')` strings** (e.g. `R('lmrobdetMM(...)')`). So the bridge is **embedded R**, not Python functions wrapping `robstattm.lmrobdetMM(...)`. |
| **Wrapper-style `robstattm.locScaleM(...)` examples** | [`docs/gsoc2026_proposal/robstatpy_tests.tex`](docs/gsoc2026_proposal/robstatpy_tests.tex) (and PDF) — test-task write-up for `locScaleM` / `scaleM` only. |
| **Future installable package** | **Not in this repo yet** — no `pyproject.toml` / `pytest` tree; that is the GSoC `robstatpy` deliverable. |

**Notebook layout:** **Part I** walks through `locScaleM`, `scaleM`, `lmrobdetMM`, `covRobMM`/`covRobRocke`, `pcaRobS` via **rpy2** (main line). **Appendix A** holds optional **pure-Python** univariate cross-checks for `locScaleM`/`scaleM` only. **Not implemented here as library wrappers:** `lmrobdetDCML`, `lmrobdet.control` as a standalone Python API, `step.lmrobdet`, `pyinit`, `rob.linear.test`, `KurtSDNew`, external packages (`pense`, `GSE`, `TSGS`), GLM functions.

More detail: [`robstattm/python/NOTEBOOKS.md`](robstattm/python/NOTEBOOKS.md).

---

## How this repo maps to the proposal

The proposal references several external files. They all live here:

| Proposal reference | File in this repo |
|---|---|
| `locScaleM` and `scaleM` wrapper + test results | [`robstattm/python/robstatpy_comparison_rpy2.ipynb`](robstattm/python/robstatpy_comparison_rpy2.ipynb) |
| Subprocess comparison notebook | [`robstattm/python/robstatpy_comparison.ipynb`](robstattm/python/robstatpy_comparison.ipynb) |
| PCRA Chapter 2 comparison (R vs Python) | [`pcra/output/Ch2_Comparison.pdf`](pcra/output/Ch2_Comparison.pdf) |
| Figures for covRobMM, lmrobdetMM, pcaRobS | [`robstattm/python/figures/`](robstattm/python/figures/) |
| PCRA Python equivalent plan | [`pcra/docs/PCRA_Python_Equivalent_Plan.md`](pcra/docs/PCRA_Python_Equivalent_Plan.md) |
| 26 RobStatTM example scripts | [`robstattm/examples-scripts/`](robstattm/examples-scripts/) |

---

## GSoC Test Tasks

The proposal required completing two test tasks before contacting mentors.
Both are implemented and validated here:

### Test 1 — `locScaleM`: Robust location and scale (M-estimator)
- **Where:** [`robstatpy_comparison_rpy2.ipynb`](robstattm/python/robstatpy_comparison_rpy2.ipynb), Section 1
- **What it does:** Wraps `RobStatTM::locScaleM()` via rpy2, and provides a pure-Python
  re-implementation using bisquare and Huber ψ-functions
- **Result:** Python outputs match R to `< 1e-4` across all 6 checks ✅

### Test 2 — `scaleM`: Robust M-scale
- **Where:** [`robstatpy_comparison_rpy2.ipynb`](robstattm/python/robstatpy_comparison_rpy2.ipynb), Section 2
- **What it does:** Wraps `RobStatTM::scaleM()` and explains how its output relates
  to `locScaleM` (scaleM returns only the dispersion; locScaleM also estimates location)
- **Result:** Python outputs match R to `< 1e-4` ✅

---

## Validation Summary

All five core RobStatTM functions wrapped and validated:

| Function | Dataset | R vs Python | Status |
|---|---|---|---|
| `locScaleM` (bisquare + huber) | alcohol | 6 checks | ✅ All pass |
| `scaleM` (bisquare + huber) | flour | 2 checks | ✅ All pass |
| `lmrobdetMM` (mopt, eff=0.95) | mineral | 3 checks | ✅ All pass |
| `covRobMM` / `covRobRocke` | wine | 2 checks | ✅ All pass |
| `pcaRobS` | bus | 2 checks | ✅ All pass |

15/15 total checks pass. Max difference: `< 1e-6`.

---

## Repository Structure

```
robstattm-pyport-AG/
│
├── docs/gsoc2026_proposal/
│   ├── proposal_v4.pdf          ← GSoC 2026 proposal (read this first)
│   └── proposal_v4.tex          ← LaTeX source
│
├── robstattm/
│   ├── python/
│   │   ├── robstatpy_comparison_rpy2.ipynb   ← rpy2 bridge notebook (test tasks here)
│   │   ├── robstatpy_comparison.ipynb         ← subprocess bridge notebook
│   │   ├── build_notebook_rpy2.py             ← script that generates the rpy2 notebook
│   │   ├── build_notebook.py                  ← script that generates the subprocess notebook
│   │   ├── figures/                           ← PNG outputs (covRobMM, lmrobdetMM, pcaRobS, scaleM)
│   │   └── NOTEBOOKS.md                       ← detailed notebook documentation
│   ├── examples-scripts/        ← 26 R example scripts from Maronna et al. (2019)
│   ├── r/                       ← helper R scripts (setup, data export)
│   └── docs/                    ← setup guide, R-to-Python conversion guide
│
└── pcra/
    ├── python/
    │   ├── ch2_foundations_demo.py   ← PCRA Chapter 2 reproduced in Python
    │   └── data/                     ← CSV data exported from R
    ├── r/                            ← original R demo scripts
    ├── tools/                        ← PDF generation utilities
    ├── output/                       ← Ch2_Comparison.pdf (R vs Python side-by-side)
    └── docs/                         ← PCRA documentation and conversion plan
```

---

## Quick Start

### To view the test results (no R needed)
The notebooks have pre-populated output cells — just open them:
```bash
pip install notebook
jupyter notebook robstattm/python/robstatpy_comparison_rpy2.ipynb
```

### To re-run from scratch (requires R + rpy2)
```bash
# Install R package
Rscript -e 'install.packages("RobStatTM")'

# Install Python dependencies
pip install rpy2 numpy pandas scipy matplotlib nbformat

# Regenerate and open
cd robstattm/python
python build_notebook_rpy2.py
jupyter notebook robstatpy_comparison_rpy2.ipynb
```

### To run the PCRA Chapter 2 demo
```bash
cd pcra/python
pip install -r requirements.txt
python ch2_foundations_demo.py
# Outputs: ../output/Ch2_Figures_Python.pdf
```

---

## Project context

- **Package being wrapped:** [RobStatTM](https://cran.r-project.org/package=RobStatTM)
  by Maronna, Martin, Yohai & Salibian-Barrera — companion to the 2019 Wiley textbook
- **R package source:** [msalibian/RobStatTM](https://github.com/msalibian/RobStatTM)
- **PCRA package:** [PCRA on CRAN](https://cran.r-project.org/package=PCRA)
- **GSoC organization:** R Project for Statistical Computing
- **Mentors:** Doug Martin (UW), Matias Salibian-Barrera (UBC), Brian Peterson
