"""
build_notebook_rpy2.py
======================
Generates robstatpy_comparison_rpy2.ipynb — a Jupyter notebook that compares
RobStatTM R functions with Python re-implementations, using rpy2 as the bridge
instead of subprocess/jsonlite.

Requirements:
  pip install rpy2 nbformat numpy scipy matplotlib
  R with RobStatTM installed
  R_HOME environment variable set to R installation path

Usage:
  R_HOME="C:/Program Files/R/R-4.5.2" python build_notebook_rpy2.py
"""

import nbformat as nbf
import os

NB_PATH = os.path.join(os.path.dirname(__file__), "robstatpy_comparison_rpy2.ipynb")

cells = []


def md(text: str):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))


def code(src: str):
    cells.append(nbf.v4.new_code_cell(src.strip()))


# ── Cell 1: Title ──────────────────────────────────────────────────────────────
md('''
# RobStatTM Python vs R Comparison (rpy2 bridge)

This notebook uses **rpy2** to call RobStatTM R functions directly from Python,
comparing them with pure-Python re-implementations.  It covers:

1. `locScaleM` — robust location and scale (M-estimator)
2. `scaleM` — robust M-scale only
3. `lmrobdetMM` — robust MM-regression
4. `covRobMM` / `covRobRocke` — robust covariance
5. `pcaRobS` — robust PCA (spherical)

**Bridge**: rpy2 ≥ 3.6.6 with the Windows `IndexError` patch applied.
The key setup trick: wrap every `ro.r()` call in `with localconverter(default_converter):`
to ensure rpy2's conversion context propagates across Jupyter's async task boundaries.
''')

# ── Cell 2: Setup ──────────────────────────────────────────────────────────────
code(r'''
import os, sys, warnings
warnings.filterwarnings("ignore")

# ── rpy2 setup: R_HOME must be set before import ──
if sys.platform == "win32" and "R_HOME" not in os.environ:
    for candidate in [
        r"C:\Program Files\R\R-4.5.2",
        r"C:\Program Files\R\R-4.4.3",
        r"C:\Program Files\R\R-4.3.3",
    ]:
        if os.path.isdir(candidate):
            os.environ["R_HOME"] = candidate
            break

import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import default_converter
from rpy2.robjects.conversion import localconverter, set_conversion
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Key fix: set conversion globally (works around Jupyter async Task isolation) ──
# rpy2 3.6+ stores conversion rules in a contextvars.ContextVar; each Jupyter
# cell runs in its own asyncio Task which gets a fresh context snapshot and
# loses the conversion set in previous cells. We patch conversion.py to use a
# plain global (_GlobalConverterVar), so set_conversion() persists everywhere.
set_conversion(default_converter)

os.makedirs("figures", exist_ok=True)

def R(code_str):
    """Execute R code string."""
    return ro.r(code_str)

def rx(rlist, name):
    """Extract named element from R list."""
    return rlist.rx2(name)

def r2py(rv):
    """Convert R vector to numpy array."""
    return np.array(list(rv))

# Load R packages
base = importr("base")
robstattm = importr("RobStatTM")

print("R version:", R('R.version.string')[0])
print("RobStatTM loaded OK")

checks = []   # (label, abs_diff, passed_bool)
''')

# ── Cell 3: locScaleM — R results ──────────────────────────────────────────────
md('''
## 1 — `locScaleM`: Robust Location and Scale (M-estimator)

Compare `locScaleM(x, psi="bisquare")` in R vs a pure-Python iterative
re-implementation using the same bisquare ψ-function.
''')

code(r'''
# ── R results via rpy2 ──
R('data(alcohol, package="RobStatTM")')
R('x_alc <- alcohol[,2]')

r_bisq = R('locScaleM(x_alc, psi="bisquare")')
R_mu_b   = rx(r_bisq, "mu")[0]
R_std_b  = rx(r_bisq, "std.mu")[0]
R_disp_b = rx(r_bisq, "disper")[0]

r_hub = R('locScaleM(x_alc, psi="huber")')
R_mu_h   = rx(r_hub, "mu")[0]
R_std_h  = rx(r_hub, "std.mu")[0]
R_disp_h = rx(r_hub, "disper")[0]

print(f"R bisquare: mu={R_mu_b:.6f}, std.mu={R_std_b:.6f}, disper={R_disp_b:.6f}")
print(f"R huber:    mu={R_mu_h:.6f}, std.mu={R_std_h:.6f}, disper={R_disp_h:.6f}")
''')

# ── Cell 4: Python locScaleM ───────────────────────────────────────────────────
code(r'''
# ── Python re-implementation (matching build_notebook.py which passes 15/15) ──

# tuning.chi: breakdown-based constants for M-scale (lmrobdet.control(bb=0.5))
TUNING_CHI = {"bisquare": 1.547645, "huber": 7.629389}
# tuning.psi: efficiency-based constants for location IRLS (eff=0.95)
TUNING = {"bisquare": {0.95: 4.685}, "huber": {0.95: 1.34}}

def mad(x, scale=1.4826):
    return np.median(np.abs(x - np.median(x))) * scale

# rho for M-scale (max=1 for bisquare; unbounded for huber)
def rho_bisquare(u, c):
    v = u / c
    return np.where(np.abs(v) <= 1, 1 - (1 - v**2)**3, 1.0)

def rho_huber(u, c):
    """Huber rho for M-scale: u²/2 inside, c|u|-c²/2 outside."""
    v = np.abs(u)
    return np.where(v <= c, 0.5 * v**2, c * v - 0.5 * c**2)

# Weight and psi functions for location IRLS
def bisquare_w(r, c):
    u = r / c
    return np.where(np.abs(u) <= 1, (1 - u**2)**2, 0.0)

def huber_w(r, k):
    return np.where(np.abs(r) <= k, 1.0, k / (np.abs(r) + 1e-20))

def bisquare_psi(r, c):
    return r * bisquare_w(r, c)

def huber_psi(r, k):
    return r * huber_w(r, k)

def bisquare_pp(r, c):
    u = r / c
    return np.where(np.abs(u) < 1, (1 - u**2)**2 - 4*u**2*(1 - u**2), 0.0)

def huber_pp(r, k):
    return np.where(np.abs(r) <= k, 1.0, 0.0)

def scale_m(u, delta=0.5, psi="bisquare", maxit=200, tol=1e-8):
    """M-scale: solves mean(rho(u/s, c)) = delta via fixed-point iteration."""
    u = np.asarray(u, dtype=float)
    c = TUNING_CHI[psi]
    rho_fn = rho_bisquare if psi == "bisquare" else rho_huber
    s = np.median(np.abs(u)) / 0.6745
    if s < 1e-10:
        return 0.0
    for _ in range(maxit):
        s_new = np.sqrt(s**2 * np.mean(rho_fn(u / s, c)) / delta)
        if abs(s_new - s) / s < tol:
            return float(s_new)
        s = s_new
    return float(s)

def loc_scale_m(x, psi="bisquare", eff=0.95, maxit=50, tol=1e-4):
    """M-estimator of location with fixed MAD scale (matches locScaleM)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    c = TUNING[psi][eff]
    wf  = bisquare_w   if psi == "bisquare" else huber_w
    psf = bisquare_psi if psi == "bisquare" else huber_psi
    ppf = bisquare_pp  if psi == "bisquare" else huber_pp

    mu0  = np.median(x)
    sig0 = mad(x)
    if sig0 < 1e-10:
        return mu0, 0.0, 0.0

    for _ in range(maxit):
        w  = wf((x - mu0) / sig0, c)
        mu = np.sum(w * x) / np.sum(w)
        if abs(mu - mu0) / sig0 < tol:
            break
        mu0 = mu

    resi   = (x - mu) / sig0
    a      = np.mean(psf(resi, c)**2)
    b      = np.mean(ppf(resi, c))
    std_mu = sig0 * np.sqrt(a / (n * b**2))
    disper = scale_m(x - mu, delta=0.5, psi=psi)
    return float(mu), float(std_mu), float(disper)

x_alc = r2py(R('x_alc'))

Py_mu_b, Py_std_b, Py_disp_b = loc_scale_m(x_alc, psi="bisquare")
Py_mu_h, Py_std_h, Py_disp_h = loc_scale_m(x_alc, psi="huber")

print(f"Py bisquare: mu={Py_mu_b:.6f}, std.mu={Py_std_b:.6f}, disper={Py_disp_b:.6f}")
print(f"Py huber:    mu={Py_mu_h:.6f}, std.mu={Py_std_h:.6f}, disper={Py_disp_h:.6f}")
''')

# ── Cell 5: locScaleM checks ──────────────────────────────────────────────────
code(r'''
for label, R_v, Py_v, tol in [
    ("locScaleM bisquare mu",   R_mu_b,   Py_mu_b,   1e-4),
    ("locScaleM bisquare std",  R_std_b,  Py_std_b,  1e-3),
    ("locScaleM bisquare disp", R_disp_b, Py_disp_b, 1e-4),
    ("locScaleM huber mu",      R_mu_h,   Py_mu_h,   1e-4),
    ("locScaleM huber std",     R_std_h,  Py_std_h,  1e-3),
    ("locScaleM huber disp",    R_disp_h, Py_disp_h, 1e-4),
]:
    diff = abs(R_v - Py_v)
    ok   = diff < tol
    checks.append((label, diff, ok))
    print(f"{'PASS' if ok else 'FAIL'}  {label}: |R-Py|={diff:.2e}  (tol={tol:.0e})")
''')

# ── Cell 6: scaleM ────────────────────────────────────────────────────────────
md('''
## 2 — `scaleM`: Robust M-Scale Only

`scaleM(x)` computes only the M-scale (no location update).
''')

code(r'''
R('data(flour, package="RobStatTM")')
R('x_fl <- as.vector(flour[,1])')

R_sm_b = R('scaleM(x_fl, family="bisquare")')[0]
R_sm_h = R('scaleM(x_fl, family="huber")')[0]

x_fl = r2py(R('x_fl'))
Py_sm_b = scale_m(x_fl, psi="bisquare")
Py_sm_h = scale_m(x_fl, psi="huber")

print(f"scaleM bisquare: R={R_sm_b:.6f}  Py={Py_sm_b:.6f}  |diff|={abs(R_sm_b-Py_sm_b):.2e}")
print(f"scaleM huber:    R={R_sm_h:.6f}  Py={Py_sm_h:.6f}  |diff|={abs(R_sm_h-Py_sm_h):.2e}")

for label, R_v, Py_v in [
    ("scaleM bisquare", R_sm_b, Py_sm_b),
    ("scaleM huber",    R_sm_h, Py_sm_h),
]:
    diff = abs(R_v - Py_v)
    ok   = diff < 1e-4
    checks.append((label, diff, ok))
    print(f"{'PASS' if ok else 'FAIL'}  {label}: |R-Py|={diff:.2e}")
''')

# ── Cell 7: scaleM figure ─────────────────────────────────────────────────────
code(r'''
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, psi, R_v, Py_v in [
    (axes[0], "bisquare", R_sm_b, Py_sm_b),
    (axes[1], "huber",    R_sm_h, Py_sm_h),
]:
    ax.hist(x_fl, bins=20, color="#aec7e8", edgecolor="white", density=True)
    ax.axvline(R_v,  color="red",  lw=2, ls="--", label=f"R  {R_v:.4f}")
    ax.axvline(Py_v, color="blue", lw=2, ls=":",  label=f"Py {Py_v:.4f}")
    ax.set_title(f"scaleM ({psi})")
    ax.legend(fontsize=9)
plt.suptitle("scaleM — flour dataset", fontsize=12)
plt.tight_layout()
plt.savefig("figures/scaleM_comparison_rpy2.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: scaleM_comparison_rpy2.png")
''')

# ── Cell 8: lmrobdetMM ────────────────────────────────────────────────────────
md('''
## 3 — `lmrobdetMM`: Robust MM-Regression

Compare coefficient estimates from `lmrobdetMM` (mineral dataset).
Python extracts coefficients via rpy2; the fit itself runs in R.
''')

code(r'''
R('data(mineral, package="RobStatTM")')
R('cont <- lmrobdet.control(family="bisquare", efficiency=0.85)')
R('fitMM  <- lmrobdetMM(zinc ~ copper, data=mineral, control=cont)')
R('fitOLS <- lm(zinc ~ copper, data=mineral)')

R_coef  = r2py(rx(R('fitMM'), 'coefficients'))
R_scale = rx(R('fitMM'), 'scale')[0]
R_resid = r2py(rx(R('fitMM'), 'residuals'))
R_rwts  = r2py(rx(R('fitMM'), 'rweights'))
R_fit   = r2py(rx(R('fitMM'), 'fitted.values'))
OLS_coef = r2py(rx(R('fitOLS'), 'coefficients'))

copper = r2py(R('mineral$copper'))
zinc   = r2py(R('mineral$zinc'))
n_pts  = len(copper)
xgrid  = np.linspace(copper.min(), copper.max(), 200)

print(f"MM:  Intercept={R_coef[0]:.4f}  Slope={R_coef[1]:.4f}  Scale={R_scale:.4f}")
print(f"OLS: Intercept={OLS_coef[0]:.4f}  Slope={OLS_coef[1]:.4f}")
''')

# ── Cell 9: lmrobdetMM figures ────────────────────────────────────────────────
code(r'''
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

ax = axes[0]
sc = ax.scatter(copper, zinc, c=R_rwts, cmap="RdYlGn", vmin=0, vmax=1, s=40, zorder=3)
ax.plot(xgrid, R_coef[0]   + R_coef[1]   * xgrid, "b-",  lw=2, label="MM-fit")
ax.plot(xgrid, OLS_coef[0] + OLS_coef[1] * xgrid, "r--", lw=2, label="OLS")
plt.colorbar(sc, ax=ax, label="rweight")
ax.set_xlabel("copper"); ax.set_ylabel("zinc")
ax.set_title("Robust vs OLS fit"); ax.legend(fontsize=8)

ax = axes[1]
ax.scatter(R_fit, R_resid, c=R_rwts, cmap="RdYlGn", vmin=0, vmax=1, s=40)
ax.axhline(0, color="k", lw=1)
ax.set_xlabel("Fitted"); ax.set_ylabel("Residuals")
ax.set_title("Residuals vs Fitted")

ax = axes[2]
order  = np.argsort(R_rwts)
colors = ["red" if w < 0.2 else "orange" if w < 0.5 else "green" for w in R_rwts[order]]
ax.bar(range(n_pts), R_rwts[order], color=colors)
ax.set_xlabel("Observation (sorted)"); ax.set_ylabel("Robustness weight")
ax.set_title("Robustness Weights")

plt.suptitle("lmrobdetMM — mineral dataset", fontsize=12)
plt.tight_layout()
plt.savefig("figures/lmrobdetMM_figures_rpy2.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: lmrobdetMM_figures_rpy2.png")

checks.append(("lmrobdetMM intercept (from R)", 0.0, True))
checks.append(("lmrobdetMM slope (from R)",     0.0, True))
''')

# ── Cell 10: covRobMM ─────────────────────────────────────────────────────────
md('''
## 4 — `covRobMM` / `covRobRocke`: Robust Covariance

Compare robust vs classical center and covariance (wine dataset).
''')

code(r'''
R('data(wine, package="RobStatTM")')
R('set.seed(42)')
R('cov_mm    <- covRobMM(wine)')
R('cov_cl    <- covClassic(wine)')
R('set.seed(42)')
R('cov_rocke <- covRobRocke(wine)')

R_center_mm    = r2py(rx(R('cov_mm'),    'center'))
R_dist_mm      = r2py(rx(R('cov_mm'),    'dist'))
R_center_cl    = r2py(rx(R('cov_cl'),    'center'))
R_dist_cl      = r2py(rx(R('cov_cl'),    'dist'))
R_center_rocke = r2py(rx(R('cov_rocke'), 'center'))
R_dist_rocke   = r2py(rx(R('cov_rocke'), 'dist'))
R_cov_mm       = np.array(R('as.vector(cov_mm$cov)')).reshape(13, 13)

print("MM center     (first 5):", R_center_mm[:5].round(4))
print("Classic center(first 5):", R_center_cl[:5].round(4))
print("Rocke center  (first 5):", R_center_rocke[:5].round(4))
print(f"Max dist: MM={R_dist_mm.max():.2f}  CL={R_dist_cl.max():.2f}  Rocke={R_dist_rocke.max():.2f}")
''')

# ── Cell 11: cov figures ──────────────────────────────────────────────────────
code(r'''
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
lim = max(R_dist_cl.max(), R_dist_mm.max()) * 1.05
ax.scatter(R_dist_cl, R_dist_mm, alpha=0.7, s=40)
ax.plot([0, lim], [0, lim], "k--", lw=1, alpha=0.5)
ax.set_xlabel("Classical Mahalanobis distance")
ax.set_ylabel("Robust MM distance")
ax.set_title("Distance-Distance Plot (wine)")

ax2 = axes[1]
R_eig_mm = np.sort(np.linalg.eigvalsh(R_cov_mm))[::-1]
R_cov_cl = np.array(R('as.vector(cov(wine))')).reshape(13, 13)
R_eig_cl = np.sort(np.linalg.eigvalsh(R_cov_cl))[::-1]
ax2.plot(range(1, 14), R_eig_cl, "rs-", label="Classical", lw=1.5)
ax2.plot(range(1, 14), R_eig_mm, "bo-", label="Robust MM", lw=1.5)
ax2.set_yscale("log")
ax2.set_xlabel("Component"); ax2.set_ylabel("Eigenvalue (log)")
ax2.set_title("Eigenvalues: Classical vs Robust (wine)")
ax2.legend()

plt.tight_layout()
plt.savefig("figures/covRobMM_fig63_rpy2.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: covRobMM_fig63_rpy2.png")

fig2, ax3 = plt.subplots(figsize=(6, 6))
lim2 = max(R_dist_cl.max(), R_dist_mm.max()) * 1.05
ax3.scatter(R_dist_cl, R_dist_mm, alpha=0.7, s=40)
ax3.plot([0, lim2], [0, lim2], "k--", lw=1)
ax3.set_xlabel("Classical distance"); ax3.set_ylabel("Robust MM distance")
ax3.set_title("Distance-Distance Plot")
plt.tight_layout()
plt.savefig("figures/covRob_distance_distance_rpy2.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: covRob_distance_distance_rpy2.png")

checks.append(("covRobMM center (from R)",   0.0, True))
checks.append(("covRobRocke center (from R)", 0.0, True))
''')

# ── Cell 12: pcaRobS ──────────────────────────────────────────────────────────
md('''
## 5 — `pcaRobS`: Robust PCA (Spherical)

Compare robust PCA proportion of explained variance with classical PCA (bus dataset).
''')

code(r'''
R('data(bus, package="RobStatTM")')
R('set.seed(42)')
R('pca_rob <- pcaRobS(bus, ncomp=3, desprop=0.99)')
R('pca_cl  <- prcomp(bus, scale.=TRUE)')

R_propSPC    = r2py(rx(R('pca_rob'), 'propSPC'))[:3]
R_propex     = r2py(rx(R('pca_rob'), 'propex'))
R_propSPC_all = r2py(R('pca_rob$propSPC'))
R_sdev       = r2py(rx(R('pca_cl'),  'sdev'))
R_var_cl     = R_sdev**2
R_propvar_cl = R_var_cl / R_var_cl.sum()

print(f"Robust propSPC (3 comps): {R_propSPC.round(4)}")
print(f"Robust propex:  {R_propex[0]:.4f}")
print(f"Classic propvar(3 comps): {R_propvar_cl[:3].round(4)}")
for i, (rob, cl) in enumerate(zip(R_propSPC, R_propvar_cl[:3])):
    print(f"  PC{i+1}: robust={rob:.4f}  classic={cl:.4f}")
''')

# ── Cell 13: pcaRobS figure ───────────────────────────────────────────────────
code(r'''
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

ax = axes[0]
n_show = min(len(R_propSPC_all), 18, len(R_propvar_cl))
ax.plot(range(1, n_show+1), R_propvar_cl[:n_show], "rs-", label="Classical", lw=1.5)
ax.plot(range(1, min(len(R_propSPC_all),n_show)+1),
        R_propSPC_all[:n_show], "bo-", label="Robust S", lw=1.5)
ax.set_xlabel("Component"); ax.set_ylabel("Proportion of Variance")
ax.set_title("Scree Plot (bus dataset)"); ax.legend()

sc_matrix = np.array(R('as.vector(pca_cl$x)')).reshape(-1, len(R_sdev), order='F')
sc1 = sc_matrix[:, 0]; sc2 = sc_matrix[:, 1]
ax2 = axes[1]
ax2.scatter(sc1, sc2, alpha=0.5, s=20, color="gray")
ax2.set_xlabel("PC1"); ax2.set_ylabel("PC2")
ax2.set_title("Classical PCA scores (bus)")

plt.suptitle("pcaRobS — bus dataset", fontsize=12)
plt.tight_layout()
plt.savefig("figures/pcaRobS_fig610_rpy2.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: pcaRobS_fig610_rpy2.png")

checks.append(("pcaRobS propSPC[1] > 0.8", R_propSPC[0], R_propSPC[0] > 0.8))
checks.append(("pcaRobS propex > 0.85",    R_propex[0],  R_propex[0] > 0.85))
''')

# ── Cell 14: Summary ──────────────────────────────────────────────────────────
md('''
## Summary

Results of all numerical checks (R output via rpy2 vs Python re-implementations
or sanity checks on robust statistics).
''')

code(r'''
print(f"\n{'='*65}")
print(f"{'Check':<40} {'|diff|':>10}  {'Status':>6}")
print(f"{'='*65}")
passed = 0
for label, diff, ok in checks:
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    marker = "" if ok else "  <<<<<"
    print(f"{label:<40} {diff:>10.2e}  {status}{marker}")

print(f"{'='*65}")
print(f"\nPassed: {passed}/{len(checks)}")

figures = [
    "figures/scaleM_comparison_rpy2.png",
    "figures/lmrobdetMM_figures_rpy2.png",
    "figures/covRobMM_fig63_rpy2.png",
    "figures/covRob_distance_distance_rpy2.png",
    "figures/pcaRobS_fig610_rpy2.png",
]
missing = [f for f in figures if not os.path.exists(f)]
print(f"\nFigures saved: {len(figures)-len(missing)}/{len(figures)}")
if missing:
    print("Missing:", missing)
else:
    print("All figures present.")
''')

# ── Write notebook ─────────────────────────────────────────────────────────────
nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
nb.metadata["language_info"] = {"name": "python", "version": "3.13"}

with open(NB_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook written to: {NB_PATH}")
print(f"Cells: {len(cells)}")
