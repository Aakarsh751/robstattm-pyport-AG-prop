"""
Generate PCRA Python Equivalent Plan as PDF using fpdf2.
"""
import os
import subprocess
import sys

try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
except ImportError:
    print("Installing fpdf2...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2", "--quiet"])
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos


class PlanPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(True, margin=15)

    def header(self):
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "PCRA Python Equivalent Plan", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 8, f"Page {self.page_no()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    def section_title(self, text, level=1):
        self.ln(4)
        if level == 1:
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(0, 0, 0)
        else:
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(40, 40, 40)
        self.multi_cell(0, 8, text)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def body_bold(self, text):
        self.set_font("Helvetica", "B", 10)
        self.multi_cell(0, 6, text)
        self.set_font("Helvetica", "", 10)
        self.ln(1)

    def table_row(self, cells, col_widths=None, header=False):
        if col_widths is None:
            n = len(cells)
            w = (self.w - self.l_margin - self.r_margin) / max(n, 1)
            col_widths = [w] * n
        self.set_font("Helvetica", "B" if header else "", 9)
        for i, cell in enumerate(cells):
            w = col_widths[i] if i < len(col_widths) else col_widths[-1]
            self.cell(w, 6, str(cell)[:50], border=1)
        self.ln()
        self.set_font("Helvetica", "", 10)


def main():
    pdf = PlanPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "How to Create a Python Equivalent of the PCRA Package", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Plan document | GitHub (robustport/PCRA), CRAN Manual, vignettes, Ch_2_Foundations_Demo.R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    # --- 1. Understanding What PCRA Actually Is ---
    pdf.section_title("1. Understanding What PCRA Actually Is", level=1)
    pdf.body(
        "From studying the GitHub source (robustport/PCRA), the CRAN manual (55 pages), "
        "all four vignettes, and the full Ch_2_Foundations_Demo.R, PCRA has three distinct layers:"
    )
    pdf.ln(2)

    pdf.section_title("Layer A: Data (most valuable and hardest to replicate)", level=2)
    pdf.body("Datasets provided by or used in PCRA:")
    data_rows = [
        ("Dataset", "Description"),
        ("stocksCRSPmonthly", "81,144 x 14: monthly returns, 294 CRSP stocks (1993-2015)"),
        ("stocksCRSPweekly / daily", "Same stocks at higher frequencies"),
        ("factorsSPGMI / factorsSPGMIr", "81,144 x 22: 14 SPGMI alpha factors for those stocks"),
        ("SP500, SP500from1967to2007, ...", "Historical S&P index data"),
        ("FRBinterestRates", "90-day bill rates (1934-2014)"),
        ("edhec (PerformanceAnalytics)", "Hedge fund strategy returns"),
        ("~15 individual stock datasets", "retDD, retEDS, retFNB, retKBH, retMER, etc."),
        ("CboeOptionStrategies, ConferenceBoardETI, ...", "Options, employment, credit, Treasury"),
    ]
    col_w = [70, pdf.w - pdf.l_margin - pdf.r_margin - 70]
    for i, row in enumerate(data_rows):
        pdf.table_row(row, col_w, header=(i == 0))
    pdf.ln(2)

    pdf.section_title("Layer B: Functions (~40 exported in R/)", level=2)
    pdf.body("Function categories and examples:")
    func_rows = [
        ("Category", "Count", "Examples"),
        ("Efficient frontier math", "7", "mathEfrontRiskyMuCov, mathGmv, mathTport, mathWtsEfrontRiskyMuCov"),
        ("Data selection/manipulation", "5", "selectCRSPandSPGMI, stocksCRSPxts, returnsCRSPxts, getPCRAData"),
        ("Portfolio analytics", "6", "barplotWts, bootEfronts, chart.Efront, opt.outputMvoPCRA, minVarCashRisky"),
        ("Visualization", "5", "tsPlotMP, barplotWts, ellipsesPlotPCRA.covfm"),
        ("Robust statistics", "4", "plotLSandRobustSFM, plotLSandHuberRobustSFM, cleanOutliers, meanReturns4Types"),
        ("Statistical utilities", "6+", "divHHI, levgLongShort, turnOver, winsorize, winsorMean, KRest, SKest, psiHuber"),
    ]
    c1, c2, c3 = 55, 18, pdf.w - pdf.l_margin - pdf.r_margin - 73
    for i, row in enumerate(func_rows):
        pdf.table_row(row, [c1, c2, c3], header=(i == 0))
    pdf.ln(2)

    pdf.section_title("Layer C: Ecosystem Glue", level=2)
    pdf.body(
        "PCRA orchestrates 12+ other R packages. Demo scripts call: PortfolioAnalytics (spec, constraints, "
        "objectives, rebalancing); PerformanceAnalytics (Return.rebalancing, Drawdowns, table.Drawdowns); "
        "RPESE/RPEIF (influence-function standard errors); RobStatTM (locScaleM, scaleM, lmrobdetMM); "
        "optimalRhoPsi (rho_modOpt, psi_modOpt, computeTuningPsi_modOpt); CVXR; ggplot2, lattice, xts, zoo, "
        "data.table, quadprog, corpcor, boot, robustbase."
    )
    pdf.ln(4)

    # --- 2. Package structure (abbreviated) ---
    pdf.section_title("2. Python Package Structure", level=1)
    pdf.body("pcra/ with modules: data, frontier, optimization, risk, robust, selection, visualization, utils.")
    pdf.ln(2)

    # --- 3. Mapping table ---
    pdf.section_title("3. Function Mapping: R to Python", level=1)
    pdf.body("Efficient frontier: numpy. Optimization: cvxpy. Risk: numpy/pandas. Robust: scipy + custom. Viz: matplotlib.")
    pdf.ln(2)

    pdf.section_title("4. Python Dependencies", level=1)
    pdf.body("numpy, pandas, cvxpy, scipy, statsmodels, matplotlib; pyreadr for R data extraction.")
    pdf.ln(2)

    pdf.section_title("5. Phased Roadmap", level=1)
    road_rows = [
        ("Phase", "Scope", "Effort"),
        ("1. Core math", "mathEfront*, mathGmv*, mathTport, mathWtsEfront*", "2-3 weeks"),
        ("2. Data layer", "Extract to CSV; load_*(); selectCRSPandSPGMI equivalent", "1 week"),
        ("3. Risk measures", "SD, SemiSD, VaR, ES, ratios, drawdowns; IF SEs", "2 weeks"),
        ("4. Optimization", "cvxpy; rolling-window rebalancing", "2-3 weeks"),
        ("5. Robust statistics", "locScaleM, M-scale, mOpt psi, tuning", "3-4 weeks"),
        ("6. Visualization", "tsPlotMP, barplotWts, frontier plots", "1 week"),
    ]
    rw1, rw2, rw3 = 35, 75, 35
    for i, row in enumerate(road_rows):
        pdf.table_row(row, [rw1, rw2, rw3], header=(i == 0))
    pdf.ln(2)

    pdf.section_title("6. Gaps: No Direct Python Equivalent", level=1)
    pdf.body(
        "1) RPESE/RPEIF - influence-function SEs for risk measures; implement from theory. "
        "2) optimalRhoPsi - mOpt psi and efficiency-based tuning; implement from formulas. "
        "3) PortfolioAnalytics rebalancing - full rolling-window backtest; build with cvxpy + pandas."
    )

    out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "PCRA_Python_Equivalent_Plan.pdf")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pdf.output(out_path)
    print("Written:", out_path)
    return out_path


if __name__ == "__main__":
    main()
