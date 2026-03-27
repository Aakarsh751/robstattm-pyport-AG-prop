# RobStatTM reproducibility

Python and R workflows for **RobStatTM** (*Robust Statistics: Theory and Methods* book examples).

## Structure

| Path | Purpose |
|------|---------|
| `RobStatTM-master/` | Cloned R package source (data in `data/`, scripts in `inst/scripts/`) |
| `examples-scripts/` | Book example `.R` scripts (flour, shock, oats, …) |
| `python/` | Python reproductions (`flour_example.py`, `shock_example.py`, extracted CSVs in `python/data/`) |
| `r/` | R helpers: `export_robstattm_data.R`, `setup_and_run_examples.R` |
| `docs/` | Study guide, conversion guide, PDFs (book, examples guide, robust statistics text) |
| `archive/` | Optional zip of the package source |

## Run (from project root `ProfDM_Rproject`)

- `Rscript robstattm/r/export_robstattm_data.R` — CSV export for Python (optional if using `pyreadr` in Python)  
- `source("robstattm/r/setup_and_run_examples.R")` — install packages & run flour/shock/oats  
- `python robstattm/python/extract_robstattm_data.py` — extract `.RData` → CSV  
- `python robstattm/python/run_reproduced_examples.py` — run Python examples  

See **`docs/RobStatTM_Study_and_Setup_Guide.md`** for full instructions.
