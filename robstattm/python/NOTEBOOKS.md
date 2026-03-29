# RobStatTM Comparison Notebooks — Technical Documentation

## Overview

Two Jupyter notebooks compare RobStatTM R functions against pure-Python
re-implementations.  They share identical Python math but use different
bridges to call R:

| Notebook | Builder | R Bridge | Status |
|---|---|---|---|
| `robstatpy_comparison.ipynb` | `build_notebook.py` | subprocess + jsonlite | 15/15 checks pass |
| `robstatpy_comparison_rpy2.ipynb` | `build_notebook_rpy2.py` | rpy2 3.6.6 | Part I = rpy2 bridge; Appendix A = univariate R vs NumPy |

---

## Approach 1 — Subprocess + jsonlite bridge

### Files

- **`build_notebook.py`** — generates the notebook programmatically
- **`robstatpy_comparison.ipynb`** — the output (24 cells, fully executed)

### How it works

```
Python → writes .R file → Rscript.exe --vanilla → stdout (JSON) → Python dict
```

#### `rjson(code)` — the bridge function

```python
def rjson(code: str) -> dict:
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".R",
                                     delete=False, encoding="utf-8") as tf:
        tf.write("library(RobStatTM)\nlibrary(jsonlite)\n" + code)
        fname = tf.name
    try:
        res = subprocess.run([RSCRIPT, "--vanilla", fname],
                             capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"R error:\n{res.stderr[:400]}")
        return json.loads(res.stdout.strip())
    finally:
        os.unlink(fname)
```

**Why temp file instead of `-e`?**
`Rscript -e "..."` on Windows silently truncates multi-line strings at the
first embedded newline.  Writing to a `.R` file avoids this entirely.

**R serialization pattern** — every R call ends with:

```r
cat(toJSON(list(
    mu    = r_bis$mu,
    disper = r_bis$disper
), digits = 15))
```

- `digits=15` preserves full double precision
- `cat()` writes to stdout; R package messages go to stderr (not captured)
- Numeric vectors serialize as flat JSON arrays (never `as.list()` — that
  produces `[[v1],[v2],...]`)
- `set.seed(42)` before any call that uses RNG (`covRobMM`, `pcaRobS`)

### How the notebook is generated

`build_notebook.py` uses **nbformat** to assemble cells in memory, then writes
the `.ipynb` file once:

```python
import nbformat as nbf

C = []
def md(src):   C.append(nbf.v4.new_markdown_cell(src))
def code(src): C.append(nbf.v4.new_code_cell(src))

md("## Section heading")
code(r'''...cell source...''')

nb = nbf.v4.new_notebook()
nb.cells = C
nbf.write(nb, open("robstatpy_comparison.ipynb", "w"))
```

Run as:

```bash
python build_notebook.py
python -m nbconvert --to notebook --execute robstatpy_comparison.ipynb \
       --output robstatpy_comparison.ipynb
```

### Notebook structure (24 cells)

| Cells | Section | Description |
|---|---|---|
| 0 | Title / intro | Markdown overview |
| 1 | Setup | Import subprocess, define `r()` / `rjson()`, verify Rscript path |
| 2–6 | locScaleM | R ground truth → Python IRLS → comparison table → checks |
| 7–10 | scaleM | R `scaleM()` → Python M-scale → figure |
| 11–13 | lmrobdetMM | R MM-regression on mineral dataset → 3-panel figure |
| 14–17 | covRobMM / covRobRocke | R robust covariance on wine → distance-distance plot + eigenvalue plot |
| 18–21 | pcaRobS | R robust PCA on bus → scree plot + score plot |
| 22–23 | Summary | 15-row check table + figure file verification |

### Key bugs fixed during development

| Bug | Root cause | Fix |
|---|---|---|
| `SyntaxError` in builder | `code(r"""...rjson("""...""")...""")` — inner `"""` closes outer string | Global replace `code(r"""` → `code(r'''` |
| Empty stdout / `JSONDecodeError` | `Rscript -e` truncates multi-line strings on Windows | Switched to temp `.R` file |
| 2-D numpy arrays | `as.list(numeric_vector)` → JSON `[[v1],[v2],...]` | Removed all `as.list()` wrappers |
| `.Random.seed not found` crash | `--vanilla` skips RNG init; `covRobMM` needs it | Added `set.seed(42)` before RNG-dependent calls |
| Wrong `disper` (0.226 vs 0.685) | Used `tuning.psi=4.685` (efficiency) instead of `tuning.chi=1.547645` (breakdown) | Added `TUNING_CHI` dict; fixed `scale_m` |
| Wrong huber disper (0.295 vs 5.309) | Normalized rho (`0.5*(u/c)²`, bounded) instead of unbounded rho | `rho_huber(u,c) = where(v≤c, v²/2, cv-c²/2)` |
| Shape `(3,)` vs `(17,)` in PCA | `pca_rob$propSPC` returns all 17 components | R code: `propSPC_rob = rr$propSPC[1:q]` |

---

## Approach 2 — rpy2 bridge

### Files

- **`build_notebook_rpy2.py`** — generates the notebook
- **`robstatpy_comparison_rpy2.ipynb`** — the output (20 cells, fully executed)

### How it works

```
Python → rpy2 → libR.so/R.dll (in-process) → R objects → Python objects
```

No subprocess.  R runs inside the same Python process via rpy2's CFFI
bindings.  R objects are exposed as Python proxy objects (`ListVector`,
`FloatVector`, etc.) and converted with `.rx2()` / `list()`.

### Installation

```bash
# Python 3.13 required (rpy2 3.6.x supports 3.9–3.13; not 3.14)
py -3.13 -m pip install rpy2
```

Set `R_HOME` before any import:

```bash
set R_HOME=C:\Program Files\R\R-4.5.2
py -3.13 your_script.py
```

Or in Python before importing rpy2:

```python
import os
os.environ["R_HOME"] = r"C:\Program Files\R\R-4.5.2"
import rpy2.robjects as ro
```

### Windows patches required

rpy2 3.6.6 has two bugs on Windows without Rtools.  Both are patched by
editing the installed files directly.

#### Patch 1 — `openrlib.py` line 23

**File:** `site-packages/rpy2/rinterface_lib/openrlib.py`

**Problem:** `R CMD config --ldflags` calls `config.sh` which internally calls
`make`.  Without Rtools, `make` is not found so the output is an empty string.
`situation/__init__.py:271` then does `output_lst[0].startswith('WARNING')`
→ `IndexError` (empty list).  `openrlib.py` catches only `CalledProcessError`,
so the fallback DLL-path logic (which would have worked) never runs.

```python
# BEFORE (line 23):
except rpy2.situation.subprocess.CalledProcessError:

# AFTER:
except (rpy2.situation.subprocess.CalledProcessError, IndexError, Exception):
```

The fallback code (lines 25–45) already correctly enumerates candidate R DLL
directories (`bin/x64`, `bin/`) — it just needed to be reachable.

#### Patch 2 — `conversion.py` lines 423–424

**File:** `site-packages/rpy2/robjects/conversion.py`

**Problem:** rpy2 3.6 stores the active converter in a
`contextvars.ContextVar`.  Jupyter's kernel creates a new `asyncio.Task` for
each cell execution.  Each Task gets a **snapshot** of the context from when
the task was created — so `ContextVar.set()` calls from cell 1's task are
invisible to cell 2's task.  This makes `get_conversion()` return the
`missingconverter` sentinel and raise `NotImplementedError`.

```python
# BEFORE:
converter_ctx = contextvars.ContextVar('converter', default=missingconverter)

# AFTER:
class _GlobalConverterVar:
    """Drop-in for ContextVar that uses a plain global (no async isolation)."""
    def __init__(self, name, *, default):
        self._name = name
        self._value = default
    def get(self, default=None):
        return self._value
    def set(self, value):
        self._value = value
        return None   # mimics Token return (ignored by callers)

converter_ctx = _GlobalConverterVar('converter', default=missingconverter)
```

`set_conversion()` and `get_conversion()` call `converter_ctx.set()` /
`.get()` respectively — no other changes needed.

**Trade-off:** The global converter is now shared across all threads.  This is
fine for single-threaded Jupyter use; for multi-threaded code that needs
per-thread converters, the ContextVar approach would be needed.

### How the notebook is generated

Same nbformat pattern as Approach 1:

```python
import nbformat as nbf
cells = []
def md(text):  cells.append(nbf.v4.new_markdown_cell(text))
def code(src): cells.append(nbf.v4.new_code_cell(src))

# ... add cells ...

nb = nbf.v4.new_notebook()
nb.cells = cells
with open("robstatpy_comparison_rpy2.ipynb", "w") as f:
    nbf.write(nb, f)
```

Run as:

```bash
R_HOME="C:/Program Files/R/R-4.5.2" py -3.13 build_notebook_rpy2.py
R_HOME="C:/Program Files/R/R-4.5.2" py -3.13 -m nbconvert \
    --to notebook --execute --ExecutePreprocessor.timeout=300 \
    robstatpy_comparison_rpy2.ipynb \
    --output robstatpy_comparison_rpy2.ipynb
```

### Key setup cell pattern

```python
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import default_converter
from rpy2.robjects.conversion import localconverter, set_conversion

# Apply Patch 2's effect: set converter globally once
set_conversion(default_converter)

# Convenience wrappers
def R(code_str):         return ro.r(code_str)
def rx(rlist, name):     return rlist.rx2(name)
def r2py(rv):            return np.array(list(rv))

base      = importr("base")
robstattm = importr("RobStatTM")
```

### R ↔ Python data flow

```
R('data(alcohol, package="RobStatTM")')   # load dataset into R global env
R('x_alc <- alcohol[,2]')                # assign in R

r_bisq = R('locScaleM(x_alc, psi="bisquare")')  # → ListVector
R_mu   = rx(r_bisq, "mu")[0]                     # → Python float
x_alc  = r2py(R('x_alc'))                        # → numpy array
```

Reshaping matrices (rpy2 returns matrices as flat column-major vectors):

```python
R_cov_mm = np.array(R('as.vector(cov_mm$cov)')).reshape(13, 13)
sc_matrix = np.array(R('as.vector(pca_cl$x)')).reshape(-1, p, order='F')
```

### Notebook structure (20 cells)

| Cells | Section | Description |
|---|---|---|
| 0 | Title / intro | Markdown overview including patch explanation |
| 1 | Setup | R_HOME detection, rpy2 import, set_conversion, importr |
| 2 | locScaleM — R | Call locScaleM for bisquare and huber via rpy2 |
| 3 | locScaleM — Python | Full Python re-implementation (loc_scale_m, scale_m) |
| 4 | locScaleM checks | 6-row comparison table |
| 5 | scaleM | R `scaleM(family=...)` vs Python `scale_m()` |
| 6 | scaleM figure | Histogram with M-scale markers, saved as PNG |
| 7 | lmrobdetMM | R MM-regression on mineral dataset |
| 8 | lmrobdetMM figures | 3-panel: scatter+fits / residuals / robustness weights |
| 9 | covRobMM | R covRobMM + covClassic + covRobRocke on wine |
| 10 | cov figures | Distance-distance plot + eigenvalue comparison |
| 11 | pcaRobS | R pcaRobS + prcomp on bus dataset |
| 12 | pcaRobS figure | Scree plot + PC1 vs PC2 score plot |
| 13 | Summary | 14-row check table + figure file verification |

### Key difference: `scaleM` argument name

R's `scaleM` uses `family=` not `psi=`:

```r
scaleM(x, family="bisquare")   # correct
scaleM(x, psi="bisquare")      # ERROR: unused argument
```

---

## Shared Python Mathematics

Both notebooks implement the same algorithms.

### `rho` functions for M-scale

```python
def rho_bisquare(u, c):
    # max = 1; E_Z[rho(Z, 1.547645)] = 0.5 for standard normal Z
    v = u / c
    return np.where(np.abs(v) <= 1, 1 - (1 - v**2)**3, 1.0)

def rho_huber(u, c):
    # unbounded; E_Z[rho(Z, 7.629389)] = 0.5 for standard normal Z
    v = np.abs(u)
    return np.where(v <= c, 0.5 * v**2, c * v - 0.5 * c**2)
```

**Critical detail:** `rho_bisquare` must have max = 1, not max = c²/6.
With c = 1.547645, `c²/6 ≈ 0.399 < 0.5 = delta`.  If max rho < delta,
the fixed-point iteration `s_new = sqrt(s² · mean(rho)/delta)` can never
satisfy `mean(rho) = delta` → iteration diverges to zero → NaN.

### `scale_m` — M-scale fixed-point iteration

```python
TUNING_CHI = {"bisquare": 1.547645, "huber": 7.629389}  # from lmrobdet.control(bb=0.5)

def scale_m(u, delta=0.5, psi="bisquare", maxit=200, tol=1e-8):
    u   = np.asarray(u, dtype=float)
    c   = TUNING_CHI[psi]
    rho = rho_bisquare if psi == "bisquare" else rho_huber
    s   = np.median(np.abs(u)) / 0.6745   # MAD-based initialisation
    if s < 1e-10: return 0.0
    for _ in range(maxit):
        s_new = np.sqrt(s**2 * np.mean(rho(u / s, c)) / delta)
        if abs(s_new - s) / s < tol: return float(s_new)
        s = s_new
    return float(s)
```

### `loc_scale_m` — IRLS location with fixed MAD scale

```python
TUNING = {"bisquare": {0.95: 4.685}, "huber": {0.95: 1.34}}  # efficiency-based

def loc_scale_m(x, psi="bisquare", eff=0.95, maxit=50, tol=1e-4):
    x    = np.asarray(x, dtype=float)
    c    = TUNING[psi][eff]
    mu0  = np.median(x)
    sig0 = mad(x)              # MAD held fixed during IRLS (not updated)
    for _ in range(maxit):
        w  = weight_fn(x - mu0) / sig0, c)
        mu = np.sum(w * x) / np.sum(w)
        if abs(mu - mu0) / sig0 < tol: break
        mu0 = mu
    std_mu = sandwich_variance(x, mu, sig0, c, n)
    disper = scale_m(x - mu, delta=0.5, psi=psi)
    return mu, std_mu, disper
```

**Key distinction:** `loc_scale_m` uses `TUNING` (efficiency-based, e.g. 4.685
for 95%-efficient bisquare) for the IRLS weight function.  `scale_m` uses
`TUNING_CHI` (breakdown-based, 1.547645) for the rho function.  These are
different constants with different purposes.

### Weight / psi functions for location IRLS

```python
def bisquare_w(r, c):    # Tukey bisquare weight
    u = r / c
    return np.where(np.abs(u) <= 1, (1 - u**2)**2, 0.0)

def huber_w(r, k):       # Huber weight
    return np.where(np.abs(r) <= k, 1.0, k / (np.abs(r) + 1e-20))
```

---

## Figures produced

All figures are saved to the `figures/` subdirectory.

| Figure | Notebook | Description |
|---|---|---|
| `figures/scaleM_comparison.png` | subprocess | Histogram of flour data with R/Py M-scale lines |
| `figures/lmrobdetMM_figures.png` | subprocess | 3-panel: scatter+fits, residuals, robustness weights |
| `figures/covRobMM_fig63.png` | subprocess | Eigenvalue comparison (classical vs robust) |
| `figures/covRob_distance_distance.png` | subprocess | Mahalanobis distance plot |
| `figures/pcaRobS_fig610.png` | subprocess | Scree plot + score biplot |
| `figures/scaleM_comparison_rpy2.png` | rpy2 | Same as above |
| `figures/lmrobdetMM_figures_rpy2.png` | rpy2 | Same as above |
| `figures/covRobMM_fig63_rpy2.png` | rpy2 | Same as above |
| `figures/covRob_distance_distance_rpy2.png` | rpy2 | Same as above |
| `figures/pcaRobS_fig610_rpy2.png` | rpy2 | Same as above |

---

## Environment

| Component | Version |
|---|---|
| Python | 3.13 |
| R | 4.5.2 |
| rpy2 | 3.6.6 (with two patches) |
| RobStatTM | installed in R |
| nbformat | any recent |
| nbconvert | any recent |
| numpy | any recent |
| matplotlib | any recent |

---

## Quick Reference

```bash
# Generate + execute subprocess notebook
python build_notebook.py
python -m nbconvert --to notebook --execute robstatpy_comparison.ipynb \
       --output robstatpy_comparison.ipynb

# Generate + execute rpy2 notebook
R_HOME="C:/Program Files/R/R-4.5.2" py -3.13 build_notebook_rpy2.py
R_HOME="C:/Program Files/R/R-4.5.2" py -3.13 -m nbconvert \
    --to notebook --execute --ExecutePreprocessor.timeout=300 \
    robstatpy_comparison_rpy2.ipynb \
    --output robstatpy_comparison_rpy2.ipynb
```
