# RobStatTM: Study and Setup Guide

This guide helps you (1) understand the RobStatTM package, (2) set up R and run the example scripts, and (3) reproduce the book examples step by step.

---

## Part 1: Understanding RobStatTM

### What is RobStatTM?

- **Official repo:** [github.com/msalibian/RobStatTM](https://github.com/msalibian/RobStatTM)
- **CRAN:** [cran.r-project.org/package=RobStatTM](https://cran.r-project.org/web/packages/RobStatTM/index.html)
- **Book:** *Robust Statistics: Theory and Methods (with R)*, 2nd ed., Maronna, Martin, Yohai, Salibian-Barrera (Wiley).

RobStatTM is the **companion R package** to the book. It provides:

- Implementations of the **robust estimators** described in the book (regression, multivariate, GLM, time series).
- **Datasets** used in the book (loaded with `data(name)` after `library(RobStatTM)`).
- **Example scripts** that reproduce the book’s figures and tables (in the package `scripts` folder and in **`robstattm/examples-scripts/`**).

### Package structure (from the GitHub repo)

| Folder / file | Purpose |
|---------------|--------|
| **R/** | R source: main functions (e.g. `lmrobdet.R`, `lmrob.MM.R`), psi/rho utilities, datasets as `.R` files. |
| **src/** | C/Fortran code for performance-critical algorithms. |
| **inst/scripts/** | Example scripts (shock.R, oats.R, flour.R, mineral.R, etc.) that reproduce book examples. |
| **data/** | Package data (often mirrored in R/*.R as data objects). |
| **man/** | R help files. |
| **vignettes/** | Longer tutorials (e.g. optimal rho/psi, fit.models). |

### Main functions you will use (from NAMESPACE)

- **Regression:** `lmrobM`, `lmrobdetMM`, `lmrobdetDCML`, `lmrobM.control`, `lmrobdet.control`, `rob.linear.test`, `step.lmrobdetMM`, `drop1.lmrobdetMM`.
- **Location/scale:** `locScaleM`, `scaleM`, `MLocDis`.
- **Multivariate:** `covClassic`, `covRob`, `covRobMM`, `covRobRocke`, `prcompRob`, `fastmve`, `SMPCA`, etc.
- **GLM:** `logregWBY`, `logregBY`, `logregWML`, `WBYlogreg`, `BYlogreg`, `WMLlogreg`.
- **Psi/rho:** `bisquare`, `huber`, `mopt`, `opt`, `rho`, `rhoprime`, `rhoprime2`.
- **Other:** `DCML`, `lsRobTestMM`, `initPP`, etc.

### Dependencies (from DESCRIPTION)

- **R:** >= 3.5.0
- **Imports:** `stats`, **pyinit**, **rrcov**, **robustbase**
- **Suggests:** R.rsp (for vignettes)

When you install RobStatTM from CRAN, **pyinit**, **rrcov**, and **robustbase** are installed automatically. Some **example scripts** need extra packages (see table in Part 3).

---

## Part 2: Step-by-step R setup

### Step 1: Install R

1. Download R for Windows: [https://cran.r-project.org/bin/windows/base/](https://cran.r-project.org/bin/windows/base/).
2. Run the installer. Use default options unless you have a reason to change them.
3. Optionally install **RStudio**: [https://posit.co/download/rstudio-desktop/](https://posit.co/download/rstudio-desktop/).

### Step 2: Install RobStatTM and required packages

Open **R** or **RStudio** and run:

```r
# Install RobStatTM from CRAN (this will also install pyinit, rrcov, robustbase)
install.packages("RobStatTM")

# Install extra packages needed by some example scripts (see Guide table)
install.packages("quantreg")   # for shock.R, mineral.R
install.packages("robustbase")  # for wood.R (data); often already installed as dependency
install.packages("rrcov")       # for vehicle.R; often already installed
# Optional, for later examples:
# install.packages("robust")      # leukemia.R, epilepsy.R
# install.packages("robustarima") # Ch 8 time series scripts
```

If any package fails, note the error (e.g. “cannot install ‘pyinit’”). On Windows, **Rtools** may be needed for packages that compile C code: [https://cran.r-project.org/bin/windows/Rtools/](https://cran.r-project.org/bin/windows/Rtools/).

### Step 3: Verify installation

Run:

```r
library(RobStatTM)
data(shock)
head(shock, 2)
# Should show: n.shocks and time columns

# Optional: find where the package scripts are installed
system.file("scripts", package = "RobStatTM")
```

If these run without errors, RobStatTM is installed correctly.

### Step 4: Use `robstattm/examples-scripts/`

This folder contains the same scripts as in the package (shock.R, oats.R, flour.R, etc.). Run them from R by setting the working directory to the project root (`ProfDM_Rproject`) and sourcing the script.

In R:

```r
# Set working directory to your project (change if your path is different)
setwd("C:/ProfDM_Rproject")

# Run an example (no extra package needed)
source("robstattm/examples-scripts/flour.R")

# Run Example 4.1 (needs quantreg)
source("robstattm/examples-scripts/shock.R")

# Run Example 4.2 (no extra package)
source("robstattm/examples-scripts/oats.R")
```

**Tip:** In RStudio: **Session → Set Working Directory → Choose Directory** and select `C:\ProfDM_Rproject`. Then `source("robstattm/examples-scripts/shock.R")` works as above.

---

## Part 3: Which script needs which package (from the Guide)

From *RobStatTM Examples Scripts and Data Sets Guide*:

| Example | Script     | Data in RobStatTM | Other package(s)     |
|---------|------------|-------------------|----------------------|
| 1.1, 2.1, Table 2.4 | flour.R   | flour             | —                    |
| 4.1     | shock.R    | shock             | **quantreg**         |
| 4.2     | oats.R     | oats              | —                    |
| 5.1     | mineral.R  | mineral           | quantreg             |
| 5.2     | wood.R     | —                 | **robustbase** (data)|
| 5.3     | step.R     | (synthetic)       | —                    |
| 5.4     | algae.R    | algae             | —                    |
| 5.5     | ExactFit.R | (synthetic)       | —                    |
| 6.1     | biochem.R  | biochem           | —                    |
| 6.2     | wine.R     | wine              | —                    |
| 6.3     | vehicle.R  | vehicle           | rrcov                |
| 6.4     | bus.R      | bus               | —                    |
| 7.1     | leukemia.R | leuk.dat          | robust               |
| 7.2     | skin.R     | skin              | —                    |
| 7.3     | epilepsy.R | breslow.dat       | robust               |
| 8.x     | ar1.R, ... | various           | robustarima          |

For **reproducing the “mentioned results”** (e.g. Ch 2 and Examples 4.1, 4.2), you need at least:

- **RobStatTM** (and hence pyinit, rrcov, robustbase).
- **quantreg** for `shock.R`.

---

## Part 4: Reproducing results (recommended order)

### 1. flour.R (Example 1.1, Figure 2.1, Table 2.4)

- **No extra package.** Uses `locScaleM()` (M-estimation of location/scale).
- **Output:** Table 2.4 (mean, bisquare M-estimate, 25% trimmed mean; SEs; 0.95 CIs).
- Run: `setwd("C:/ProfDM_Rproject"); source("robstattm/examples-scripts/flour.R")`.

### 2. shock.R (Example 4.1, Figures 4.1 & 4.3, Table 4.1)

- **Requires:** `quantreg` (for L1 fit with `quantreg::rq()`).
- **Output:** Two plots (LS vs LS without outliers; LS, LS-, L1, M lines) and coefficient table.
- Run: `source("robstattm/examples-scripts/shock.R")`.
- If you see “M-step did NOT converge”, try increasing `max.it` or relaxing `rel.tol` in `lmrobdet.control()` (see Guide, last page).

### 3. oats.R (Example 4.2, Figures 4.2 & 4.4)

- **No extra package.** Uses `lm()` and `lmrobM()` with factors, `anova()`, `rob.linear.test()`.
- **Output:** Residual plot (Figure 4.2), QQ plot of standardized residuals (Figure 4.4), and matrix of classical vs robust p-values.
- Run: `source("robstattm/examples-scripts/oats.R")`.
- **Note:** Guide says p-values and some plot details may differ slightly from the book due to later code changes; conclusions on outliers remain the same.

### 4. mineral.R, wood.R, algae.R, etc.

- Proceed in the order of the Guide table. Install any “OTHER PACKAGES REQUIRED” before running the script (e.g. `quantreg` for mineral.R, `robustbase` for wood.R for data).

---

## Part 5: Quick reference – running all example scripts from R

From your project root (e.g. `C:\ProfDM_Rproject`), you can run:

```r
setwd("C:/ProfDM_Rproject")
scripts_dir <- file.path("robstattm", "examples-scripts")

# Easiest (no extra packages)
source(file.path(scripts_dir, "flour.R"))
source(file.path(scripts_dir, "oats.R"))

# Needs quantreg
source(file.path(scripts_dir, "shock.R"))
```

Use the same pattern for other scripts once the required packages are installed.

---

## Part 6: If something goes wrong

- **“there is no package called ‘X’”**  
  Run `install.packages("X")`. If X is pyinit, rrcov, or robustbase, installing RobStatTM usually installs them; if not, install X first, then RobStatTM.

- **“M-step did NOT converge”**  
  Use a larger `max.it` or smaller `rel.tol` in `lmrobdet.control()` / `lmrobM.control()` (see Guide, convergence section).

- **Script can’t find data**  
  Ensure `library(RobStatTM)` was run and that you’re using the correct data name (e.g. `data(shock)` for shock.R). Data come from the package, not from the script file.

- **Plots or numbers differ from the book**  
  The Guide states that some scripts produce slightly different p-values or plot details; conclusions are typically unchanged.

---

## Summary

1. **RobStatTM** = R package for the book *Robust Statistics: Theory and Methods*; install from CRAN; dependencies (pyinit, rrcov, robustbase) install automatically.
2. **Setup:** Install R → `install.packages("RobStatTM")` → `install.packages("quantreg")` (and others as needed).
3. **`robstattm/examples-scripts/`** has the same scripts as the package; run them with `source("robstattm/examples-scripts/<script>.R")` after `setwd("C:/ProfDM_Rproject")`.
4. **Reproduce results** by running flour.R, then shock.R (with quantreg), then oats.R, then the rest in the order of the Guide table.

For full details on the package, see the [RobStatTM GitHub repo](https://github.com/msalibian/RobStatTM) and the [RobStatTM Examples Scripts and Data Sets Guide](RobStatTM%20Examples%20Scripts%20and%20Data%20Sets%20Guide.pdf).
