"""
Ch_2_Foundations_Demo.py
========================
Python reproduction of the R script Ch_2_Foundations_Demo.R from the PCRA package.
Reproduces key Figures (2.1-2.5, 2.16, 2.25, 2.30, 2.31, 2.36, 2.38)
and Tables (2.1-2.8) from Chapter 2: Foundations.

Data is loaded from CSV files previously extracted from R via extract_pcra_data.R.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import median_abs_deviation, kurtosis
from numpy.random import dirichlet

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
PDF_OUT = os.path.join(SCRIPT_DIR, "..", "output", "Ch2_Figures_Python.pdf")


# ---------------------------------------------------------------------------
# Helper: two-asset efficient frontier (replicates R's efront2Asset)
# ---------------------------------------------------------------------------
def efront_2asset(wts, rho, mu_vol=(0.20, 0.10, 0.15, 0.04)):
    sigma1, mu1, sigma2, mu2 = mu_vol
    w = np.asarray(wts)
    mu = w * mu1 + (1 - w) * mu2
    var = (w ** 2 * sigma1 ** 2
           + 2 * w * (1 - w) * rho * sigma1 * sigma2
           + (1 - w) ** 2 * sigma2 ** 2)
    sigma = np.sqrt(var)
    return pd.DataFrame({"SIGMA": sigma, "MU": mu, "WTS": w})


# ---------------------------------------------------------------------------
# Helper: mathematical efficient frontier from mu, vol, corr (risky only)
# ---------------------------------------------------------------------------
def math_efront_risky_mu_cov(mu_ret, vol_ret, corr_ret, npoints=100,
                              efront_only=True):
    mu_ret = np.asarray(mu_ret, dtype=float)
    vol_ret = np.asarray(vol_ret, dtype=float)
    corr_ret = np.asarray(corr_ret, dtype=float)
    V = np.diag(vol_ret) @ corr_ret @ np.diag(vol_ret)
    Vinv = np.linalg.inv(V)
    one = np.ones(len(mu_ret))
    a = mu_ret @ Vinv @ one
    b = mu_ret @ Vinv @ mu_ret
    c = one @ Vinv @ one
    d = b * c - a ** 2
    mu_gmv = a / c
    sigma_gmv = 1 / np.sqrt(c)
    mu_max = max(mu_ret)
    mu_range = np.linspace(mu_gmv, mu_max * 1.2, npoints)
    sigma_range = np.sqrt((c * mu_range ** 2 - 2 * a * mu_range + b) / d)
    if not efront_only:
        mu_full = np.linspace(mu_gmv - (mu_max - mu_gmv), mu_max * 1.2, npoints)
        sigma_full = np.sqrt((c * mu_full ** 2 - 2 * a * mu_full + b) / d)
        return mu_range, sigma_range, mu_full, sigma_full, mu_gmv, sigma_gmv
    return mu_range, sigma_range, mu_gmv, sigma_gmv


def math_gmv_mu_cov(mu_ret, vol_ret, corr_ret):
    mu_ret = np.asarray(mu_ret, dtype=float)
    vol_ret = np.asarray(vol_ret, dtype=float)
    corr_ret = np.asarray(corr_ret, dtype=float)
    V = np.diag(vol_ret) @ corr_ret @ np.diag(vol_ret)
    Vinv = np.linalg.inv(V)
    one = np.ones(len(mu_ret))
    c_val = one @ Vinv @ one
    wts = (Vinv @ one) / c_val
    mu_gmv = mu_ret @ wts
    sigma_gmv = np.sqrt(wts @ V @ wts)
    return {"wts": wts, "mu": mu_gmv, "sigma": sigma_gmv}


def math_wts_efront_risky_mu_cov(mu_ret, vol_ret, corr_ret, mu_efront):
    mu_ret = np.asarray(mu_ret, dtype=float)
    vol_ret = np.asarray(vol_ret, dtype=float)
    corr_ret = np.asarray(corr_ret, dtype=float)
    V = np.diag(vol_ret) @ corr_ret @ np.diag(vol_ret)
    Vinv = np.linalg.inv(V)
    one = np.ones(len(mu_ret))
    z1 = Vinv @ one
    z2 = Vinv @ mu_ret
    a = mu_ret @ z1
    b = mu_ret @ z2
    c_val = one @ z1
    d = b * c_val - a ** 2
    wts_list = []
    sigmas = []
    for mu_e in mu_efront:
        w = z1 * (b - a * mu_e) / d + z2 * (c_val * mu_e - a) / d
        wts_list.append(w)
        sigmas.append(np.sqrt(w @ V @ w))
    n = len(mu_ret)
    cols = [f"W{i+1}" for i in range(n)]
    df = pd.DataFrame(wts_list, columns=cols)
    df.insert(0, "VOL", [round(s, 3) for s in sigmas])
    df.insert(0, "MU", [round(m, 3) for m in mu_efront])
    return df.round(3)


# ---------------------------------------------------------------------------
# Robust location M-estimator (bisquare psi, approximates R's locScaleM)
# ---------------------------------------------------------------------------
def loc_scale_m_bisquare(x, c_tune=4.685, maxit=50, tol=1e-6):
    x = np.asarray(x, dtype=float).ravel()
    n = len(x)
    mu = np.median(x)
    s = median_abs_deviation(x, scale="normal")
    if s < 1e-12:
        s = np.std(x) * 1.4826
    for _ in range(maxit):
        r = (x - mu) / s
        w = np.where(np.abs(r) <= c_tune, (1 - (r / c_tune) ** 2) ** 2, 0.0)
        w_sum = w.sum()
        if w_sum < 1e-12:
            break
        mu_new = (w * x).sum() / w_sum
        if abs(mu_new - mu) < tol * s:
            break
        mu = mu_new
    disper = median_abs_deviation(x - mu, scale="normal")
    std_mu = disper / np.sqrt(n)
    return {"mu": mu, "std_mu": std_mu, "disper": disper}


# ---------------------------------------------------------------------------
# Drawdown analysis
# ---------------------------------------------------------------------------
def compute_drawdowns(returns_series):
    cum = (1 + returns_series).cumprod()
    running_max = cum.cummax()
    dd = cum / running_max - 1
    return dd


def table_drawdowns(returns_df, top=2):
    results = []
    for col in returns_df.columns:
        dd = compute_drawdowns(returns_df[col])
        trough_idx = dd.idxmin()
        trough_val = dd.min()
        before_trough = dd.loc[:trough_idx]
        start_mask = before_trough == 0
        if start_mask.any():
            from_idx = before_trough[start_mask].index[-1]
        else:
            from_idx = before_trough.index[0]
        after_trough = dd.loc[trough_idx:]
        end_mask = after_trough == 0
        if end_mask.any():
            to_idx = after_trough[end_mask].index[0]
        else:
            to_idx = after_trough.index[-1]
        months = len(returns_df.loc[from_idx:to_idx])
        results.append({
            "Portfolio": col,
            "Begin": str(from_idx)[:10],
            "Minimum": str(trough_idx)[:10],
            "End": str(to_idx)[:10],
            "Months": months,
            "Depth": round(trough_val, 2),
        })
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Risk measures with standard errors (IFiid approximation)
# ---------------------------------------------------------------------------
def sd_se(returns):
    sd = returns.std()
    n = len(returns)
    k = kurtosis(returns, fisher=True)
    se = sd * np.sqrt((k + 2) / (4 * n))
    return sd, se


def semi_sd_se(returns):
    neg = returns[returns < 0]
    ssd = np.sqrt((neg ** 2).mean()) if len(neg) > 0 else 0.0
    n = len(returns)
    se = ssd / np.sqrt(2 * n)
    return ssd, se


def var_historical(returns, alpha=0.05):
    return -np.percentile(returns, alpha * 100)


def es_historical(returns, alpha=0.05):
    cutoff = np.percentile(returns, alpha * 100)
    tail = returns[returns <= cutoff]
    return -tail.mean() if len(tail) > 0 else -cutoff


# ---------------------------------------------------------------------------
# mOpt and Huber psi/rho functions (for Figure 2.36)
# ---------------------------------------------------------------------------
def rho_huber(x, cc=1.345):
    x = np.asarray(x, dtype=float)
    return np.where(np.abs(x) < cc, 0.5 * x ** 2, cc * np.abs(x) - 0.5 * cc ** 2)


def psi_huber(x, cc=1.345):
    x = np.asarray(x, dtype=float)
    return np.clip(x, -cc, cc)


def rho_modopt(x, cc):
    """Approximation of the modOpt rho function."""
    x = np.asarray(x, dtype=float)
    u = x / cc
    return np.where(np.abs(u) <= 1,
                    3 * u ** 2 - 3 * u ** 4 + u ** 6,
                    1.0) * (cc ** 2 / 2)


def psi_modopt(x, cc):
    """Derivative of rho_modopt."""
    x = np.asarray(x, dtype=float)
    u = x / cc
    return np.where(np.abs(u) <= 1,
                    x * (6 - 12 * u ** 2 + 6 * u ** 4) / (cc ** 2),
                    0.0) * (cc ** 2 / 2)


def wgt_modopt(x, cc):
    """Weight function w(x) = psi(x)/x for modOpt."""
    x = np.asarray(x, dtype=float)
    u = x / cc
    w = np.where(np.abs(u) <= 1,
                 (1 - u ** 2) ** 2 * (1 + 2 * u ** 2),
                 0.0)
    return w


def wgt_huber(x, cc=1.345):
    x = np.asarray(x, dtype=float)
    return np.where(np.abs(x) < cc, 1.0, cc / np.abs(np.where(x == 0, 1e-12, x)))


# ---------------------------------------------------------------------------
# MAD-based robust scale M-estimator (approximation of scaleM with mopt)
# ---------------------------------------------------------------------------
def scale_m_mopt(x):
    return median_abs_deviation(x, scale="normal")


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    pp = PdfPages(PDF_OUT)
    banner = lambda t: print(f"\n{'='*60}\n  {t}\n{'='*60}")

    banner("Ch 2 Foundations Demo – Python Reproduction")
    print(f"Data directory: {DATA_DIR}\n")

    # -------------------------------------------------------------------
    # Figure 2.1
    # -------------------------------------------------------------------
    print("--- Figure 2.1: Two-asset efficient frontier (rho=0) ---")
    mu_vol = (0.20, 0.10, 0.15, 0.04)
    wts = np.arange(0, 1.01, 0.01)
    ef = efront_2asset(wts, 0, mu_vol)
    gmv = ef.loc[ef["SIGMA"].idxmin()]

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(ef["SIGMA"], ef["MU"], "k-", lw=2)
    ax.plot([mu_vol[0], mu_vol[2]], [mu_vol[1], mu_vol[3]], "ko", ms=8)
    ax.plot(gmv["SIGMA"], gmv["MU"], "ko", ms=8)
    ax.set_xlim(0, 0.25); ax.set_ylim(0.03, 0.11)
    ax.set_xlabel(r"$\sigma_P$", fontsize=14)
    ax.set_ylabel(r"$\mu_P$", fontsize=14)
    ax.text(0.04, 0.10, r"$\rho = 0$", fontsize=14)
    ax.text(0.12, 0.0616, "MinRisk", ha="right", fontsize=10)
    ax.text(0.13, 0.0616, f"({gmv['SIGMA']:.2f}, {gmv['MU']:.4f})", fontsize=10)
    ax.text(0.20, 0.10, "  (0.20, 0.10)", fontsize=10)
    ax.text(0.15, 0.04, "  (0.15, 0.04)", fontsize=10)
    ax.set_title("Figure 2.1")
    fig.tight_layout(); pp.savefig(fig); plt.close(fig)
    print(f"  GMV: sigma={gmv['SIGMA']:.4f}, mu={gmv['MU']:.4f}")

    # -------------------------------------------------------------------
    # Figure 2.2
    # -------------------------------------------------------------------
    print("--- Figure 2.2: Efront with rho = -1, 0, +1 ---")
    ef0 = efront_2asset(wts, 0, mu_vol)
    ef1 = efront_2asset(wts, 1, mu_vol)
    ef_neg1 = efront_2asset(wts, -1, mu_vol)
    gmv0 = ef0.loc[ef0["SIGMA"].idxmin()]
    gmv_neg1 = ef_neg1.loc[ef_neg1["SIGMA"].idxmin()]

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(ef0["SIGMA"], ef0["MU"], "k-", lw=2)
    ax.plot(ef1["SIGMA"], ef1["MU"], "k--", lw=2)
    ax.plot(ef_neg1["SIGMA"], ef_neg1["MU"], "k--", lw=2)
    ax.plot([mu_vol[0], mu_vol[2]], [mu_vol[1], mu_vol[3]], "ko", ms=8)
    ax.plot(gmv0["SIGMA"], gmv0["MU"], "ko", ms=8)
    ax.plot(gmv_neg1["SIGMA"], gmv_neg1["MU"], "ko", ms=8)
    ax.set_xlim(0, 0.25); ax.set_ylim(0.03, 0.11)
    ax.set_xlabel(r"$\sigma_P$", fontsize=14)
    ax.set_ylabel(r"$\mu_P$", fontsize=14)
    ax.text(0.12, 0.07, r"$\rho = 0$", ha="right", fontsize=14)
    ax.text(0.02, 0.08, r"$\rho = -1$", fontsize=14)
    ax.text(0.18, 0.07, r"$\rho = +1$", fontsize=14)
    ax.set_title("Figure 2.2")
    fig.tight_layout(); pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Figure 2.3
    # -------------------------------------------------------------------
    print("--- Figure 2.3: Long-only vs short-selling ---")
    wts_lo = np.arange(0, 1.01, 0.01)
    wts_ss = np.arange(1, 1.26, 0.01)
    ef_lo = efront_2asset(wts_lo, 0, mu_vol)
    ef_ss = efront_2asset(wts_ss, 0, mu_vol)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(ef_lo["SIGMA"], ef_lo["MU"], "k-", lw=2)
    ax.plot(ef_ss["SIGMA"], ef_ss["MU"], "k--", lw=2)
    gmv_lo = ef_lo.loc[ef_lo["SIGMA"].idxmin()]
    max_mu_lo = ef_lo.loc[ef_lo["MU"].idxmax()]
    max_mu_ss = ef_ss.loc[ef_ss["MU"].idxmax()]
    for pt in [gmv_lo, max_mu_lo, max_mu_ss]:
        ax.plot(pt["SIGMA"], pt["MU"], "ko", ms=8)
        ax.annotate(f"({pt['SIGMA']:.2f}, {pt['MU']:.2f})",
                    (pt["SIGMA"], pt["MU"]), textcoords="offset points",
                    xytext=(10, 0), fontsize=9)
    ax.set_xlim(0, 0.40); ax.set_ylim(0.02, 0.13)
    ax.set_xlabel(r"$\sigma_P$", fontsize=14)
    ax.set_ylabel(r"$\mu_P$", fontsize=14)
    ax.text(0.04, 0.12, r"$\rho = 0$", fontsize=14)
    ax.set_title("Figure 2.3")
    fig.tight_layout(); pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Figure 2.4
    # -------------------------------------------------------------------
    print("--- Figure 2.4: Three-asset pairwise efronts ---")
    vm1 = (0.20, 0.10); vm2 = (0.15, 0.04); vm3 = (0.10, 0.02)
    wts04 = np.arange(0, 1.01, 0.01)
    ef12 = efront_2asset(wts04, 0, vm1 + vm2)
    ef13 = efront_2asset(wts04, 0, vm1 + vm3)
    ef23 = efront_2asset(wts04, 0, vm2 + vm3)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(ef12["SIGMA"], ef12["MU"], "k-", lw=2)
    ax.plot(ef13["SIGMA"], ef13["MU"], "k--", lw=2)
    ax.plot(ef23["SIGMA"], ef23["MU"], "k:", lw=2)
    for v, m in [vm1, vm2, vm3]:
        ax.plot(v, m, "ko", ms=8)
        ax.annotate(f"({v}, {m})", (v, m), textcoords="offset points",
                    xytext=(10, 0), fontsize=10)
    ax.set_xlim(0, 0.25); ax.set_ylim(0, 0.11)
    ax.set_xlabel(r"$\sigma_P$", fontsize=14)
    ax.set_ylabel(r"$\mu_P$", fontsize=14)
    ax.text(0.04, 0.10, r"$\rho = 0$", fontsize=14)
    ax.set_title("Figure 2.4")
    fig.tight_layout(); pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Figure 2.5
    # -------------------------------------------------------------------
    print("--- Figure 2.5: Random portfolios in risk-return space ---")
    vol = np.array([0.20, 0.15, 0.10])
    mu = np.array([0.10, 0.04, 0.02])
    cov_mat = np.diag(vol) @ np.eye(3) @ np.diag(vol)
    np.random.seed(42)
    wts_rand = dirichlet(np.ones(3), 500)
    port_sig = np.array([np.sqrt(w @ cov_mat @ w) for w in wts_rand])
    port_mu = wts_rand @ mu

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(port_sig, port_mu, s=10, c="gray", alpha=0.6)
    ax.plot(vol, mu, "ko", ms=8)
    for v, m in zip(vol, mu):
        ax.annotate(f"({v}, {m})", (v, m), textcoords="offset points",
                    xytext=(10, 0), fontsize=10)
    ax.set_xlim(0, 0.25); ax.set_ylim(0, 0.11)
    ax.set_xlabel(r"$\sigma_P$", fontsize=14)
    ax.set_ylabel(r"$\mu_P$", fontsize=14)
    ax.text(0.04, 0.10, r"$\rho = 0$", fontsize=14)
    ax.set_title("Figure 2.5")
    fig.tight_layout(); pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Example 2.3
    # -------------------------------------------------------------------
    print("\n--- Example 2.3: GMV from mu and cov ---")
    mu_ret = [0.10, 0.04, 0.02]
    vol_ret = [0.20, 0.15, 0.10]
    corr_ret = np.eye(3)
    gmv_result = math_gmv_mu_cov(mu_ret, vol_ret, corr_ret)
    print(f"  GMV weights: {np.round(gmv_result['wts'], 3)}")
    print(f"  GMV mean:    {gmv_result['mu']:.3f}")
    print(f"  GMV vol:     {gmv_result['sigma']:.3f}")

    # -------------------------------------------------------------------
    # Figure 2.16
    # -------------------------------------------------------------------
    print("\n--- Figure 2.16: Efront (risky assets) ---")
    mu_e, sig_e, mu_full, sig_full, mu_g, sig_g = math_efront_risky_mu_cov(
        mu_ret, vol_ret, corr_ret, npoints=100, efront_only=False)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(sig_full, mu_full, "k--", lw=1, alpha=0.5)
    ax.plot(sig_e, mu_e, "k-", lw=2)
    ax.plot(sig_g, mu_g, "ko", ms=8)
    ax.text(sig_g + 0.005, mu_g, "GMV", fontsize=10)
    ax.set_xlabel(r"$\sigma_P$", fontsize=14)
    ax.set_ylabel(r"$\mu_P$", fontsize=14)
    ax.set_title("Figure 2.16 – Efficient Frontier")
    fig.tight_layout(); pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Table 2.4
    # -------------------------------------------------------------------
    print("\n--- Table 2.4: Efront weights ---")
    mu_efront_vals = np.linspace(mu_g, max(mu_ret) * 1.2, 5)
    wts_table = math_wts_efront_risky_mu_cov(mu_ret, vol_ret, corr_ret, mu_efront_vals)
    print(wts_table.to_string(index=False))

    # -------------------------------------------------------------------
    # Load CRSP data for Figures 2.7–2.12 and Tables 2.1–2.3
    # -------------------------------------------------------------------
    ret10_path = os.path.join(DATA_DIR, "returns10Mkt.csv")
    wts_path = os.path.join(DATA_DIR, "wtsGmvLS.csv")
    retcomb_path = os.path.join(DATA_DIR, "ret_comb.csv")

    if os.path.isfile(ret10_path):
        print("\n--- Loading CRSP data ---")
        ret10 = pd.read_csv(ret10_path, parse_dates=["Date"], index_col="Date")
        print(f"  returns10Mkt: {ret10.shape}")
        stocks = ret10.columns[:10].tolist()
        print(f"  Stocks: {stocks}")

        # Figure 2.7
        print("\n--- Figure 2.7: 10 SmallCap stocks + Market time series ---")
        fig, axes = plt.subplots(6, 2, figsize=(12, 14), sharex=True)
        for i, col in enumerate(ret10.columns[:11]):
            r, c_idx = divmod(i, 2)
            ax = axes[r, c_idx]
            ax.plot(ret10.index, ret10[col], "k-", lw=0.5)
            ax.set_title(col, fontsize=9)
            ax.axhline(0, color="gray", lw=0.5, ls=":")
        if len(ret10.columns) < 12:
            axes[5, 1].set_visible(False)
        fig.suptitle("Figure 2.7 – SmallCap Stocks & Market Returns", fontsize=12)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        pp.savefig(fig); plt.close(fig)

    if os.path.isfile(wts_path):
        wts_df = pd.read_csv(wts_path, parse_dates=["Date"], index_col="Date")
        print(f"  wtsGmvLS: {wts_df.shape}")

        # Figure 2.8
        print("--- Figure 2.8: GmvLS portfolio weights over time ---")
        fig, axes = plt.subplots(5, 2, figsize=(12, 12), sharex=True)
        for i, col in enumerate(wts_df.columns[:10]):
            r, c_idx = divmod(i, 2)
            ax = axes[r, c_idx]
            ax.plot(wts_df.index, wts_df[col], "k-", lw=0.8)
            ax.set_title(col, fontsize=9)
        fig.suptitle("Figure 2.8 – GmvLS Weights", fontsize=12)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        pp.savefig(fig); plt.close(fig)

    if os.path.isfile(retcomb_path):
        ret_comb = pd.read_csv(retcomb_path, parse_dates=["Date"], index_col="Date")
        print(f"  ret_comb: {ret_comb.shape}")

        # Figure 2.9
        print("--- Figure 2.9: GmvLS and Market returns ---")
        fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        for i, col in enumerate(ret_comb.columns):
            axes[i].plot(ret_comb.index, ret_comb[col], "k-", lw=0.7)
            axes[i].set_title(col, fontsize=10)
            axes[i].axhline(0, color="gray", lw=0.5, ls=":")
        fig.suptitle("Figure 2.9 – GmvLS & Market Returns", fontsize=12)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        pp.savefig(fig); plt.close(fig)

        # Figure 2.10
        print("--- Figure 2.10: Cumulative returns & drawdowns ---")
        cum_ret = (1 + ret_comb).cumprod()
        dd = pd.DataFrame()
        for col in ret_comb.columns:
            dd[col] = compute_drawdowns(ret_comb[col])

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True,
                                        gridspec_kw={"height_ratios": [2, 1]})
        ax1.plot(cum_ret.index, cum_ret["GmvLS"], "k-", lw=1.5, label="GmvLS")
        ax1.plot(cum_ret.index, cum_ret["Market"], "darkred", lw=1.5, ls="--", label="Market")
        ax1.set_title("Cumulative Returns")
        ax1.legend(loc="upper left")
        ax2.plot(dd.index, dd["GmvLS"], "darkblue", lw=1.5, label="GmvLS")
        ax2.plot(dd.index, dd["Market"], "darkred", lw=1.5, ls="--", label="Market")
        ax2.set_title("Drawdowns")
        ax2.legend(loc="lower left")
        fig.suptitle("Figure 2.10", fontsize=12)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        pp.savefig(fig); plt.close(fig)

        # Table 2.1
        print("\n--- Table 2.1: Drawdowns ---")
        dd_table = table_drawdowns(ret_comb, top=2)
        print(dd_table.to_string(index=False))

        # Table 2.2
        print("\n--- Table 2.2: Risk measures with standard errors ---")
        risk_rows = []
        for col in ret_comb.columns:
            r = ret_comb[col].values
            sd_val, sd_err = sd_se(r)
            ssd_val, ssd_err = semi_sd_se(r)
            es_val = es_historical(r)
            var_val = var_historical(r)
            risk_rows.append([f"{col} SD",  round(sd_val * 100, 2), round(sd_err * 100, 2)])
            risk_rows.append([f"{col} SSD", round(ssd_val * 100, 2), round(ssd_err * 100, 2)])
            risk_rows.append([f"{col} ES",  round(es_val * 100, 2), "—"])
            risk_rows.append([f"{col} VaR", round(var_val * 100, 2), "—"])
        risk_df = pd.DataFrame(risk_rows, columns=["Measure", "Estimate (%)", "StdError (%)"])
        print(risk_df.to_string(index=False))

        # Table 2.3
        print("\n--- Table 2.3: Performance ratios ---")
        for col in ret_comb.columns:
            r = ret_comb[col].values
            sr = r.mean() / r.std() if r.std() > 0 else 0
            print(f"  {col} Sharpe Ratio: {sr:.3f}")

    # -------------------------------------------------------------------
    # Figure 2.25
    # -------------------------------------------------------------------
    print("\n--- Figure 2.25: Leverage and expected return ---")
    rf = 0.03; rf_lend = 0.04; rf_borrow = 0.06; er_port = 0.07
    leverage = np.arange(0, 2.1, 0.1)
    er_rf = rf + leverage * (er_port - rf)
    er_1 = rf_lend + leverage * (er_port - rf_lend)
    er_2 = rf_borrow + leverage * (er_port - rf_borrow)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(leverage, er_rf, "b-", lw=1.5, label="Single Rf for Borrow & Lend")
    ax.plot(leverage, np.minimum(er_1, er_2), "r--", lw=1.5, label="Different Rf for Borrow & Lend")
    ax.set_xlabel("Leverage", fontsize=12)
    ax.set_ylabel("Expected Return", fontsize=12)
    ax.legend(fontsize=10)
    ax.set_title("Figure 2.25")
    fig.tight_layout(); pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Figure 2.30
    # -------------------------------------------------------------------
    print("--- Figure 2.30: Utility functions ---")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    x = np.arange(0.01, 3.01, 0.01)
    ax1.plot(x, np.log(x), "k-", lw=1, label="Log Utility")
    ax1.plot(x, (x ** 0.5 - 1) / 0.5, "k:", lw=1, label=r"$\gamma = 0.5$")
    ax1.plot(x, (x ** (-0.5) - 1) / (-0.5), "k--", lw=1, label=r"$\gamma = -0.5$")
    ax1.axhline(0, color="gray", lw=0.3)
    ax1.axvline(0, color="gray", lw=0.3)
    ax1.set_ylim(-8, 2); ax1.set_xlabel("v"); ax1.set_ylabel("U(v)")
    ax1.legend(fontsize=9)

    v = np.arange(0, 1.51, 0.01)
    ax2.plot(v, v - v ** 2, "k-", lw=1.5)
    ax2.axvline(0.5, ls=":", color="gray"); ax2.axhline(0.25, ls=":", color="gray")
    ax2.set_xlabel("v"); ax2.set_ylabel("U(v)")
    ax2.set_ylim(-0.7, 0.4)
    fig.suptitle("Figure 2.30 – Power & Quadratic Utility", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Figure 2.31
    # -------------------------------------------------------------------
    print("--- Figure 2.31: CAPM Security Market Line ---")
    rm1 = 0.18
    Beta1 = [1.53, 1.36, 1.24, 1.17, 1.06, 0.92, 0.84, 0.76, 0.63, 0.48]
    Mu1 = [0.26, 0.22, 0.21, 0.21, 0.18, 0.17, 0.16, 0.15, 0.13, 0.12]
    SML1 = [rm1 * b for b in Beta1]

    rm2 = 0.08
    Beta2 = [1.50, 1.30, 1.17, 1.09, 1.03, 0.95, 0.87, 0.78, 0.67, 0.51]
    Mu2 = [0.06, 0.08, 0.08, 0.08, 0.08, 0.08, 0.07, 0.07, 0.07, 0.06]
    SML2 = [rm2 * b for b in Beta2]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.scatter(Beta1, Mu1, c="k", s=30)
    ax1.plot(Beta1, SML1, "gray", lw=1)
    ax1.plot(1.0, rm1, "^", color="dodgerblue", ms=10)
    ax1.set_xlabel("Beta"); ax1.set_ylabel("Mean Excess Return")
    ax1.set_title("1931 – 1965")
    ax1.annotate("CAPM SML", (1.19, 0.15), fontsize=9, color="gray")
    ax1.annotate("Market Portfolio", (0.78, 0.185), fontsize=9, color="dodgerblue")

    ax2.scatter(Beta2, Mu2, c="k", s=30)
    ax2.plot(Beta2, SML2, "gray", lw=1)
    ax2.plot(1.0, rm2, "^", color="dodgerblue", ms=10)
    ax2.set_xlabel("Beta"); ax2.set_ylabel("Mean Excess Return")
    ax2.set_title("1965 – 1991"); ax2.set_ylim(0, 0.12)
    ax2.annotate("CAPM SML", (1.12, 0.055), fontsize=9, color="gray")
    ax2.annotate("Market Portfolio", (0.80, 0.095), fontsize=9, color="dodgerblue")
    fig.suptitle("Figure 2.31 – CAPM Security Market Line", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Table 2.6
    # -------------------------------------------------------------------
    print("\n--- Table 2.6: Historical excess returns ---")
    table26 = pd.DataFrame({
        "Period": ["1/31–12/39", "1/40–12/49", "1/50–12/59",
                   "1/60–12/69", "1/70–12/79", "1/80–12/91"],
        "Mean(Excess)": [-0.05, 0.03, 0.08, 0.03, 0.01, 0.09],
        "StdDev(Excess)": [0.17, 0.10, 0.06, 0.07, 0.10, 0.08],
        "t(Mean)": [-0.94, 1.06, 4.25, 1.32, 0.18, 3.90],
    })
    print(table26.to_string(index=False))

    # -------------------------------------------------------------------
    # Figure 2.36
    # -------------------------------------------------------------------
    print("\n--- Figure 2.36: mOpt and Huber rho/psi ---")
    cc_huber = 1.345
    cc_modopt = 1.06  # approximate 95% efficiency tuning constant for modOpt
    x_psi = np.arange(-5, 5.01, 0.01)
    rho_max = rho_modopt(3, cc_modopt).max()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(x_psi, rho_modopt(x_psi, cc_modopt) / rho_max, "k-", lw=1.3, label="mOpt")
    ax1.plot(x_psi, rho_huber(x_psi, cc_huber) / rho_max, "darkred", ls="--", lw=1.3, label="Huber")
    ax1.set_ylabel(r"$\rho(x)$"); ax1.set_ylim(0, 2); ax1.legend()

    ax2.plot(x_psi, psi_modopt(x_psi, cc_modopt), "k-", lw=1.3, label="mOpt")
    ax2.plot(x_psi, psi_huber(x_psi, cc_huber), "darkred", ls="--", lw=1.3, label="Huber")
    ax2.set_ylabel(r"$\psi(x)$"); ax2.set_ylim(-2.5, 2.5); ax2.legend()
    fig.suptitle("Figure 2.36 – mOpt and Huber rho/psi", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Figure 2.37
    # -------------------------------------------------------------------
    print("--- Figure 2.37: mOpt and Huber weight functions ---")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_psi, wgt_modopt(x_psi, cc_modopt), "k-", lw=1, label="mOpt")
    ax.plot(x_psi, wgt_huber(x_psi, cc_huber), "darkred", ls="--", lw=1, label="Huber")
    ax.set_ylabel("w(x)"); ax.set_ylim(0, 1.45); ax.legend()
    ax.set_title("Figure 2.37 – Weight Functions")
    fig.tight_layout(); pp.savefig(fig); plt.close(fig)

    # -------------------------------------------------------------------
    # Figure 2.38 and Table 2.7
    # -------------------------------------------------------------------
    edhec_path = os.path.join(DATA_DIR, "edhec.csv")
    if os.path.isfile(edhec_path):
        print("\n--- Figure 2.38 & Table 2.7: Robust vs sample mean (FIA) ---")
        edhec = pd.read_csv(edhec_path, parse_dates=["Date"], index_col="Date")
        fia = edhec.loc["1998-01-31":"1999-12-31", "FIA"]

        mu_classic = 100 * fia.mean()
        se_classic = 100 * fia.std() / np.sqrt(len(fia))
        rob = loc_scale_m_bisquare(fia.values)
        mu_rob = 100 * rob["mu"]
        se_rob = 100 * rob["std_mu"]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(fia.index, fia.values, "ko-", ms=4, lw=0.8)
        ax.axhline(rob["mu"], color="blue", lw=1, label="Robust Mean")
        ax.axhline(fia.mean(), color="red", ls="--", lw=1, label="Sample Mean")
        ax.set_ylabel("FIA Returns"); ax.legend()
        ax.set_title("Figure 2.38 – Robust vs Sample Mean for FIA")
        fig.tight_layout(); pp.savefig(fig); plt.close(fig)

        tstat_c = mu_classic / se_classic
        tstat_r = mu_rob / se_rob
        sr_c = tstat_c / np.sqrt(24)
        sr_r = tstat_r / np.sqrt(24)
        print("  Table 2.7:")
        t27 = pd.DataFrame({
            "Estimate (%)": [round(mu_classic, 2), round(mu_rob, 2)],
            "Std. Error (%)": [round(se_classic, 2), round(se_rob, 2)],
            "t-Stat": [round(tstat_c, 2), round(tstat_r, 2)],
            "Sharpe Ratio": [round(sr_c, 2), round(sr_r, 2)],
        }, index=["Sample Mean", "Robust Mean"])
        print(t27)

    # -------------------------------------------------------------------
    # Table 2.8
    # -------------------------------------------------------------------
    if os.path.isfile(edhec_path):
        print("\n--- Table 2.8: Scale estimators on edhec ---")
        edhec_full = pd.read_csv(edhec_path, parse_dates=["Date"], index_col="Date")
        edhec12 = edhec_full.iloc[:, :12]
        ret_sub = 100 * edhec12.loc["1998-01-31":"1999-12-31"]
        std_dev = ret_sub.std()
        madm = ret_sub.apply(lambda col: median_abs_deviation(col, scale="normal"))
        rob_sd = ret_sub.apply(scale_m_mopt)
        scale_df = pd.DataFrame({
            "HFindex": ret_sub.columns,
            "StdDev": std_dev.round(2).values,
            "MADM": madm.round(2).values,
            "RobSD": rob_sd.round(2).values,
        })
        print(scale_df.to_string(index=False))

    # -------------------------------------------------------------------
    # Close PDF
    # -------------------------------------------------------------------
    pp.close()
    banner(f"All figures saved to {PDF_OUT}")
    print("Python reproduction of Ch 2 Foundations Demo complete.\n")


if __name__ == "__main__":
    main()
