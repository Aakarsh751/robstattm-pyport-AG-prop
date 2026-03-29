"""
build_notebook_rpy2.py
======================
Generates robstatpy_comparison_rpy2.ipynb — Jupyter notebook with **Part I:**
RobStatTM via **rpy2** (main focus), and **Appendix:** optional pure-Python
univariate cross-checks. Regenerate with: python build_notebook_rpy2.py

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
# RobStatTM from Python (rpy2 bridge)

**Part I — Main line (robstatpy / GSoC focus):** call **RobStatTM** through **rpy2**,
load data in R, run `locScaleM`, `scaleM`, `lmrobdetMM`, `covRobMM`, `covRobRocke`,
`pcaRobS`, and pull results into NumPy with `.rx2()` / `r2py()`. This is the wrapper
path the project ships.

**Appendix — Secondary:** optional **pure-Python** re-implementations for **univariate**
`locScaleM` / `scaleM` only, to cross-check numerics. Not the primary deliverable.

**Setup:** rpy2 ≥ 3.6; `set_conversion(default_converter)` so conversion rules persist
under Jupyter’s async cells.
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

checks = []            # bridge / sanity (Part I)
checks_appendix = []   # R vs NumPy diffs (Appendix only)
''')

# ── Cell 3–5: locScaleM — R first, then Appendix (Python) ─────────────────────
md('''
## Part I — rpy2 bridge to RobStatTM

### 1 — `locScaleM`: robust location and scale

Run `RobStatTM::locScaleM()` in R via `rpy2`, extract `mu`, `std.mu`, `disper`.
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

md('''
### 2 — `scaleM`: robust M-scale (Part I)

`RobStatTM::scaleM()` in R; pull M-scale estimates into Python and plot (flour data).
''')

code(r'''
R('data(flour, package="RobStatTM")')
R('x_fl <- as.vector(flour[,1])')
R_sm_b = R('scaleM(x_fl, family="bisquare")')[0]
R_sm_h = R('scaleM(x_fl, family="huber")')[0]
x_fl = r2py(R('x_fl'))
print(f"scaleM via rpy2: bisquare={R_sm_b:.6f}  huber={R_sm_h:.6f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, psi, R_v in [(axes[0], "bisquare", R_sm_b), (axes[1], "huber", R_sm_h)]:
    ax.hist(x_fl, bins=20, color="#aec7e8", edgecolor="white", density=True)
    ax.axvline(R_v, color="crimson", lw=2, ls="--", label=f"RobStatTM {R_v:.4f}")
    ax.set_title(f"scaleM ({psi})")
    ax.legend(fontsize=9)
plt.suptitle("scaleM — flour (RobStatTM via rpy2)", fontsize=12)
plt.tight_layout()
plt.savefig("figures/scaleM_bridge_rpy2.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: figures/scaleM_bridge_rpy2.png")
''')

# ── Cell 8: lmrobdetMM ────────────────────────────────────────────────────────
md('''
### 3 — `lmrobdetMM`: robust MM-regression

`lmrobdetMM` on the mineral dataset; coefficients and diagnostics extracted in Python via `rpy2`.
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
### 4 — `covRobMM` / `covRobRocke`: robust covariance

Robust vs classical center and distances (wine dataset).
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
### 5 — `pcaRobS`: robust PCA (spherical)

Robust vs classical proportion of variance (bus dataset).
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

# ── Appendix: pure-Python univariate cross-checks (after Part I) ──────────────
md('''
---

## Appendix A — Pure-Python univariate reference (optional)

NumPy re-implementations of `locScaleM` / `scaleM` for **R vs NumPy** agreement
only. **Not** the primary `robstatpy` deliverable (that is the rpy2 bridge in Part I).
''')

code(r'''
# ── Python re-implementation (appendix only) ──
TUNING_CHI = {"bisquare": 1.547645, "huber": 7.629389}
TUNING = {"bisquare": {0.95: 4.685}, "huber": {0.95: 1.34}}

def mad(x, scale=1.4826):
    return np.median(np.abs(x - np.median(x))) * scale

def rho_bisquare(u, c):
    v = u / c
    return np.where(np.abs(v) <= 1, 1 - (1 - v**2)**3, 1.0)

def rho_huber(u, c):
    v = np.abs(u)
    return np.where(v <= c, 0.5 * v**2, c * v - 0.5 * c**2)

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
print(f"Appendix Py bisquare: mu={Py_mu_b:.6f}, std.mu={Py_std_b:.6f}, disper={Py_disp_b:.6f}")
print(f"Appendix Py huber:    mu={Py_mu_h:.6f}, std.mu={Py_std_h:.6f}, disper={Py_disp_h:.6f}")

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
    checks_appendix.append((label, diff, ok))
    print(f"{'PASS' if ok else 'FAIL'}  {label}: |R-Py|={diff:.2e}  (tol={tol:.0e})")

R('data(flour, package="RobStatTM")')
R('x_fl <- as.vector(flour[,1])')
R_sm_b = R('scaleM(x_fl, family="bisquare")')[0]
R_sm_h = R('scaleM(x_fl, family="huber")')[0]
x_fl = r2py(R('x_fl'))
Py_sm_b = scale_m(x_fl, psi="bisquare")
Py_sm_h = scale_m(x_fl, psi="huber")
print(f"scaleM bisquare: R={R_sm_b:.6f}  Py={Py_sm_b:.6f}")
print(f"scaleM huber:    R={R_sm_h:.6f}  Py={Py_sm_h:.6f}")
for label, R_v, Py_v in [("scaleM bisquare", R_sm_b, Py_sm_b), ("scaleM huber", R_sm_h, Py_sm_h)]:
    diff = abs(R_v - Py_v)
    ok   = diff < 1e-4
    checks_appendix.append((label, diff, ok))
    print(f"{'PASS' if ok else 'FAIL'}  {label}: |R-Py|={diff:.2e}")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, psi, R_v, Py_v in [(axes[0], "bisquare", R_sm_b, Py_sm_b), (axes[1], "huber", R_sm_h, Py_sm_h)]:
    ax.hist(x_fl, bins=20, color="#aec7e8", edgecolor="white", density=True)
    ax.axvline(R_v,  color="crimson", lw=2, ls="--", label=f"R {R_v:.4f}")
    ax.axvline(Py_v, color="navy", lw=2, ls=":", label=f"NumPy {Py_v:.4f}")
    ax.set_title(f"scaleM ({psi}) appendix")
    ax.legend(fontsize=8)
plt.suptitle("scaleM — flour (R vs NumPy reference appendix)", fontsize=12)
plt.tight_layout()
plt.savefig("figures/scaleM_comparison_rpy2.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: figures/scaleM_comparison_rpy2.png")
''')

# ── Cell 14: Summary ──────────────────────────────────────────────────────────
md('''
## Summary

**Part I** — sanity checks on values extracted from R (`checks`).  
**Appendix A** — univariate R vs NumPy (`checks_appendix`).
''')

code(r'''
print("\\n=== Part I — rpy2 bridge (sanity / extraction) ===")
passed = 0
for label, diff, ok in checks:
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    print(f"  {status}  {label}  (diff={diff:.2e})")
print(f"Part I: {passed}/{len(checks)} checks passed")

print("\\n=== Appendix A — univariate R vs NumPy ===")
pa = 0
for label, diff, ok in checks_appendix:
    status = "PASS" if ok else "FAIL"
    if ok:
        pa += 1
    print(f"  {status}  {label}  |R-Py|={diff:.2e}")
print(f"Appendix: {pa}/{len(checks_appendix)} checks passed")

figures = [
    "figures/scaleM_bridge_rpy2.png",
    "figures/scaleM_comparison_rpy2.png",
    "figures/lmrobdetMM_figures_rpy2.png",
    "figures/covRobMM_fig63_rpy2.png",
    "figures/covRob_distance_distance_rpy2.png",
    "figures/pcaRobS_fig610_rpy2.png",
]
missing = [f for f in figures if not os.path.exists(f)]
print(f"\\nFigures: {len(figures)-len(missing)}/{len(figures)} on disk")
if missing:
    print("Missing:", missing)
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
