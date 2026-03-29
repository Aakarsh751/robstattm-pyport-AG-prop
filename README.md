# robstattm-pyport-AG

**Companion repository for the GSoC 2026 proposal: RobStatTMPY (Python wrappers for RobStatTM)**
Aakarsh Gupta · University of Washington · April 2026

---

## What this repo is

This repository was built to **support and demonstrate** the GSoC 2026 project proposal
[`docs/gsoc2026_proposal/proposal_v4.pdf`](docs/gsoc2026_proposal/proposal_v4.pdf).

The proposal describes building **RobStatTMPY** — a Python library that wraps the
[RobStatTM](https://cran.r-project.org/package=RobStatTM) R package, making its
robust statistical estimators (MM-regression, robust covariance, robust PCA, and more)
available to Python users with no R knowledge required.

Everything in this repo is working, runnable code produced **before the GSoC period starts**,
to demonstrate readiness for the project.

### rpy2 bridge (what lives in this repo)

| What | Where |
|------|--------|
| **Main notebook** | [`robstattm/python/robstatpy_comparison_rpy2.ipynb`](robstattm/python/robstatpy_comparison_rpy2.ipynb) — loads `rpy2`, `importr("RobStatTM")`, `set_conversion(default_converter)`, helpers `R()`, `rx()`, `r2py()`. |
| **Calling style** | Fits are run with **`R('...')`** (R code strings), not `robstattm.lmrobdetMM(...)`-style calls. The **installable RobStatTMPY** package (`pip install robstattmpy`) will expose proper Python wrappers. |
| **GSoC test tasks (write-up)** | [`docs/gsoc2026_proposal/robstatpy_tests.pdf`](docs/gsoc2026_proposal/robstatpy_tests.pdf) — `locScaleM` / `scaleM` examples and validation. |
| **Installable package** | **Not here yet** — no `pyproject.toml` / `pytest`; **RobStatTMPY** is the GSoC deliverable. |

**Notebook layout:** **Part I** = `locScaleM`, `scaleM`, `lmrobdetMM`, `covRobMM`/`covRobRocke`, `pcaRobS` via **rpy2**. **Appendix A** = optional NumPy univariate cross-checks only. **Not in this notebook as wrappers:** `lmrobdetDCML`, standalone `lmrobdet.control`, `step.lmrobdet`, `pyinit`, `rob.linear.test`, `KurtSDNew`, `pense` / `GSE` / `TSGS`, GLM.

More: [`robstattm/python/NOTEBOOKS.md`](robstattm/python/NOTEBOOKS.md).

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
- **Where:** [`robstatpy_comparison_rpy2.ipynb`](robstattm/python/robstatpy_comparison_rpy2.ipynb), **Part I §1**; optional NumPy cross-check in **Appendix A**
- **What it does:** `RobStatTM::locScaleM()` via rpy2; appendix compares to a NumPy reference
- **Result:** R vs NumPy agreement within stated tolerances on the appendix checks ✅

### Test 2 — `scaleM`: Robust M-scale
- **Where:** Same notebook, **Part I §2** (bridge) and **Appendix A** (R vs NumPy)
- **What it does:** `RobStatTM::scaleM()` via rpy2; relationship to `locScaleM` as in the book
- **Result:** Appendix checks pass ✅

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
│   └── proposal_v4.pdf          ← GSoC 2026 proposal (PDF only on this repo)
│
├── robstattm/
│   ├── python/
│   │   ├── robstatpy_comparison_rpy2.ipynb   ← rpy2 bridge notebook (main)
│   │   ├── robstatpy_comparison.ipynb         ← subprocess comparison (alternate)
│   │   ├── figures/                           ← PNG outputs
│   │   └── NOTEBOOKS.md                       ← short notebook overview
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
pip install rpy2 numpy pandas scipy matplotlib

cd robstattm/python
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
