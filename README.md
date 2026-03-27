# robstattm-pyport-AG

**Python port and reproducibility project for the RobStatTM R package**
*Google Summer of Code 2026 — Aakarsh Gupta*

---

## Overview

[RobStatTM](https://cran.r-project.org/package=RobStatTM) is an R package implementing
state-of-the-art robust statistical estimators — MM-regression, S-estimators for covariance
matrices, robust PCA, and more — as described in:

> Maronna, Martin, Yohai & Salibian-Barrera (2019).
> *Robust Statistics: Theory and Methods (with R)*, 2nd ed. Wiley.

This repository contains:
1. **Python wrappers** for RobStatTM functions via `rpy2` (primary approach)
2. **Pure-Python re-implementations** of `locScaleM` and `scaleM` as GSoC test tasks
3. **Comparison notebooks** validating Python outputs against R (15/15 checks pass)
4. **PCRA Chapter 2 reproduction** — portfolio analytics demo in Python
5. **GSoC 2026 proposal** (`docs/gsoc2026_proposal/`)

---

## Repository Structure

```
robstattm-pyport-AG/
├── robstattm/
│   ├── python/
│   │   ├── robstatpy_comparison.ipynb       # Subprocess bridge: R vs Python
│   │   ├── robstatpy_comparison_rpy2.ipynb  # rpy2 bridge: R vs Python
│   │   ├── build_notebook.py                # Regenerates the subprocess notebook
│   │   ├── build_notebook_rpy2.py           # Regenerates the rpy2 notebook
│   │   ├── figures/                         # Generated comparison figures (PNG)
│   │   └── NOTEBOOKS.md                     # Detailed notebook documentation
│   ├── examples-scripts/                    # 26 R example scripts from the textbook
│   ├── r/                                   # Helper R scripts (setup, data export)
│   └── docs/                                # Setup and conversion guides (Markdown)
│
├── pcra/
│   ├── python/
│   │   ├── ch2_foundations_demo.py          # Chapter 2 reproduction in Python
│   │   └── data/                            # CSV data extracted from R
│   ├── r/                                   # Original R demo scripts
│   ├── tools/                               # PDF generation utilities
│   ├── output/                              # R vs Python comparison PDFs
│   └── docs/                                # PCRA documentation and plan
│
└── docs/
    └── gsoc2026_proposal/
        ├── proposal_v2.pdf                  # GSoC 2026 proposal (compiled)
        └── proposal_v2.tex                  # LaTeX source
```

---

## Quick Start

### Requirements

- Python 3.9+
- R 4.3+ with `RobStatTM` installed: `install.packages("RobStatTM")`
- Python packages: `pip install rpy2 numpy pandas scipy matplotlib nbformat`

### Run the comparison notebooks

```bash
# View existing results (no R needed — output cells are pre-populated)
jupyter notebook robstattm/python/robstatpy_comparison_rpy2.ipynb

# Regenerate from scratch (requires R + rpy2)
cd robstattm/python
python build_notebook_rpy2.py
jupyter notebook robstatpy_comparison_rpy2.ipynb
```

### Run the PCRA Chapter 2 demo

```bash
cd pcra/python
pip install -r requirements.txt
python ch2_foundations_demo.py
# Output: ../output/Ch2_Figures_Python.pdf
```

---

## Validation Results

| Function | Dataset | Checks | Result |
|---|---|---|---|
| `locScaleM` (bisquare + huber) | alcohol | 6/6 | ✅ Pass |
| `scaleM` (bisquare + huber) | flour | 2/2 | ✅ Pass |
| `lmrobdetMM` | mineral | 3/3 | ✅ Pass |
| `covRobMM` / `covRobRocke` | wine | 2/2 | ✅ Pass |
| `pcaRobS` | bus | 2/2 | ✅ Pass |

All differences `< 1e-6`. Full results in the notebooks.

---

## GSoC 2026 Proposal

The compiled proposal PDF is at
[`docs/gsoc2026_proposal/proposal_v2.pdf`](docs/gsoc2026_proposal/proposal_v2.pdf).

**Mentors:** Doug Martin (UW), Matias Salibian-Barrera (UBC), Brian Peterson

---

## Related

- [msalibian/RobStatTM](https://github.com/msalibian/RobStatTM) — official R package source
- [PCRA on CRAN](https://cran.r-project.org/package=PCRA) — Portfolio Construction & Risk Analysis
