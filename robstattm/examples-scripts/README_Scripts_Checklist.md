# Examples Scripts – Checklist and Package Requirements

**These scripts are for the RobStatTM package and book — not for PCRA.** (PCRA demos are in `pcra/r/`.)

Use this with **RobStatTM Examples Scripts and Data Sets Guide.pdf** (in `robstattm/docs/`).  
Install packages from the "Other package" column before running each script.

| Script       | Book example / figure      | Other package | Run when |
|-------------|-----------------------------|---------------|----------|
| flour.R     | 1.1, Fig 2.1, Table 2.4     | —             | First (no deps) |
| shock.R     | 4.1, Fig 4.1, 4.3, Table 4.1 | **quantreg**  | After installing quantreg |
| oats.R      | 4.2, Fig 4.2, 4.4           | —             | Anytime |
| mineral.R   | 5.1                         | quantreg      | |
| wood.R      | 5.2                         | robustbase    | |
| step.R      | 5.3                         | —             | |
| algae.R     | 5.4                         | —             | |
| ExactFit.R  | 5.5                         | —             | |
| biochem.R   | 6.1                         | —             | |
| wine.R      | 6.2                         | —             | |
| vehicle.R   | 6.3                         | rrcov         | |
| bus.R       | 6.4                         | —             | |
| wine1.R     | 6.5–6.6                     | GSE           | |
| autism.R    | 6.7                         | WWGbook, robustvarComp, nlme | |
| leukemia.R  | 7.1                         | robust        | |
| skin.R      | 7.2                         | —             | |
| epilepsy.R  | 7.3                         | robust        | |
| ar1.R       | 8.1                         | robustarima   | |
| ar3.R       | 8.2                         | robustarima   | |
| identAR2.R  | 8.3                         | robustarima   | |
| identMA1.R  | 8.4                         | robustarima   | |
| MA1-AO.R    | 8.5                         | robustarima   | |
| resex.R     | 8.6                         | robustarima   | |

**How to run (from project root in R):**
```r
setwd("C:/ProfDM_Rproject")
source("robstattm/examples-scripts/flour.R")
source("robstattm/examples-scripts/shock.R")   # after install.packages("quantreg")
source("robstattm/examples-scripts/oats.R")
```

Or run the full setup script once: `source("robstattm/r/setup_and_run_examples.R")`.
