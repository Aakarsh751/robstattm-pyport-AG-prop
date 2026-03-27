# PCRA reproducibility

Chapter 2 **Foundations** demo and materials for the **PCRA** R package (portfolio construction & risk analysis).

## Structure

| Path | Purpose |
|------|---------|
| `r/` | `Ch_2_Foundations_Demo.R` (original), `run_ch2_demo.R`, `install_ch2_deps.R`, `extract_pcra_data.R` |
| `python/` | `ch2_foundations_demo.py`, `requirements.txt`, CSV data in `python/data/` (from R export) |
| `docs/` | PCRA manuals (CRAN, reproducibility, data overview, CRSP/SPGMI), Python-equivalent plan (`.md` + `.pdf`) |
| `tools/` | `make_pcra_plan_pdf.py` — regenerates the plan PDF into `docs/` |
| `output/` | `Ch2_Figures.pdf` (R), `Ch2_Figures_Python.pdf` (Python), `Ch2_Comparison.pdf` (side-by-side) |

## Run (from project root)

All paths assume working directory is **`ProfDM_Rproject`**.

1. **Install R deps:** `source("pcra/r/install_ch2_deps.R")`  
2. **Export data for Python:** `source("pcra/r/extract_pcra_data.R")`  
3. **R figures:** `source("pcra/r/run_ch2_demo.R")` → `pcra/output/Ch2_Figures.pdf`  
4. **Python figures:** `python pcra/python/ch2_foundations_demo.py` → `pcra/output/Ch2_Figures_Python.pdf`  

## Side-by-Side Comparison PDF

`python pcra/tools/make_comparison_pdf.py` builds **`pcra/output/Ch2_Comparison.pdf`**
(16 pages, one per figure, R output left / Python output right).
Requires the source PDFs to exist first (steps 3 and 4 above).

## Plan PDF

`python pcra/tools/make_pcra_plan_pdf.py` writes **`pcra/docs/PCRA_Python_Equivalent_Plan.pdf`**.
