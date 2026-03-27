"""
make_comparison_pdf.py
======================
Builds a single side-by-side PDF comparing R and Python outputs for
Chapter 2 of the PCRA package demo.

Each output page shows:
    ┌──────────── Figure X.X – Description ─────────────────┐
    │  R  [Library]  {annotations found}  │  Python  (matplotlib)  │
    │  (Ch2_Figures.pdf)                  │  (Ch2_Figures_Python.pdf) │
    └─────────────────────────────────────┴────────────────────────────┘

Run from project root:
    python pcra/tools/make_comparison_pdf.py
"""

import os
import fitz  # PyMuPDF

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.join(SCRIPT_DIR, "..")
OUTPUT_DIR  = os.path.join(ROOT_DIR, "output")

R_PDF_PATH  = os.path.join(OUTPUT_DIR, "Ch2_Figures.pdf")
PY_PDF_PATH = os.path.join(OUTPUT_DIR, "Ch2_Figures_Python.pdf")
OUT_PATH    = os.path.join(OUTPUT_DIR, "Ch2_Comparison.pdf")

# ---------------------------------------------------------------------------
# Page mapping:
#   (label, r_page_0idx, py_page_0idx, r_library)
#
# r_library describes the R graphics system used to produce each figure.
# None page index = no equivalent on that side (show placeholder).
#
# R library key:
#   "Base R"           – par/plot/lines/points/text (grDevices)
#   "lattice"          – PCRA::tsPlotMP (wraps lattice trellis panels)
#   "xts"              – plot.xts / addSeries / addLegend (xts pkg)
#   "ggplot2"          – ggplot / geom_* / theme_bw
#   "zoo + Base R"     – plot.zoo (zoo pkg, rendered via base graphics engine)
# ---------------------------------------------------------------------------
PAIRS = [
    # (label,                                                             r_idx, py_idx, r_library)
    ("Figure 2.1  -  Two-Asset Efficient Frontier (rho = 0)",               0,    0,  "Base R"),
    ("Figure 2.2  -  Two-Asset Efficient Frontier (rho = -1, 0, +1)",       1,    1,  "Base R"),
    ("Figure 2.3  -  Long-Only vs Short-Selling Frontier",                  2,    2,  "Base R"),
    ("Figure 2.4  -  Three-Asset Pairwise Frontiers",                       3,    3,  "Base R"),
    ("Figure 2.5  -  Random Portfolios in Risk-Return Space",               4,    4,  "Base R"),
    ("Figure 2.7  -  SmallCap Stock Returns (1997-2010)",                   5,    6,  "lattice"),
    ("Figure 2.8  -  GmvLS Portfolio Weights Over Time",                    6,    7,  "lattice"),
    ("Figure 2.9  -  GmvLS & Market Returns",                               7,    8,  "lattice"),
    ("Figure 2.10 -  Cumulative Returns & Drawdowns",                       8,    9,  "xts"),
    ("Figure 2.16 -  Efficient Frontier (Three Risky Assets)",              9,    5,  "Base R"),
    ("Figure 2.25 -  Leverage and Expected Return",                         10,   10, "ggplot2"),
    ("Figure 2.30 -  Utility Functions (Power & Quadratic)",                11,   11, "Base R"),
    ("Figure 2.31 -  CAPM Security Market Line",                            12,   12, "ggplot2"),
    ("Figure 2.36 -  mOpt and Huber rho / psi Functions",                  13,   13, "Base R"),
    ("Figure 2.37 -  mOpt and Huber Weight Functions w(x)",                 None, 14, "—"),
    ("Figure 2.38 -  Robust vs Sample Mean (FIA Returns)",                  14,   15, "zoo + Base R"),
]

# ---------------------------------------------------------------------------
# Layout constants  (PDF user-units = points, 72 pt/inch)
# ---------------------------------------------------------------------------
PAGE_W      = 1440   # 20 in wide
PAGE_H      = 832    # 11.6 in tall
HEADER_H    = 50     # title banner
SUBLABEL_H  = 30     # library / language sub-header strip
ANNOT_H     = 22     # annotation note strip (bottom of R column)
MARGIN      = 10
DIVIDER_W   = 2
RENDER_DPI  = 120

# Colours
C_HEADER_BG  = (0.13, 0.22, 0.42)   # dark navy
C_HEADER_FG  = (1.0,  1.0,  1.0)
C_BASE_R     = (0.85, 0.93, 0.97)   # light steel blue
C_LATTICE    = (0.83, 0.92, 0.84)   # light green
C_GGPLOT2    = (0.97, 0.91, 0.83)   # light amber
C_XTS        = (0.93, 0.87, 0.97)   # light lavender
C_ZOO        = (0.97, 0.93, 0.87)   # light wheat
C_PY         = (0.97, 0.97, 0.88)   # light yellow
C_NONE       = (0.91, 0.91, 0.91)   # grey placeholder
C_ANNOT_BG   = (0.96, 0.99, 0.96)   # very light green annotation strip
C_DIVIDER    = (0.55, 0.55, 0.55)

LIBRARY_COLORS = {
    "Base R":       C_BASE_R,
    "lattice":      C_LATTICE,
    "ggplot2":      C_GGPLOT2,
    "xts":          C_XTS,
    "zoo + Base R": C_ZOO,
    "—":            C_NONE,
}

# ---------------------------------------------------------------------------
# Annotation extraction: pull Symbol-font glyphs (Greek letters) from R page
# ---------------------------------------------------------------------------
def extract_symbol_annotations(page):
    """Return list of Symbol-font text spans found on page (Greek letters etc.)."""
    annotations = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span["font"] == "Symbol" and span["text"].strip():
                    annotations.append(span["text"].strip())
    return annotations


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def _fill_rect(page, rect, color):
    page.draw_rect(rect, color=None, fill=color, width=0)


def _centered_text(page, rect, text, fontsize, font_name="helv", color=(0, 0, 0)):
    font = fitz.Font(font_name)
    text_w = font.text_length(text, fontsize=fontsize)
    x = rect.x0 + max(0, (rect.width - text_w) / 2)
    y = rect.y0 + rect.height * 0.70
    tw = fitz.TextWriter(page.rect)
    tw.append((x, y), text, fontsize=fontsize, font=font)
    tw.write_text(page, color=color)


def _placeholder(page, rect, message):
    _fill_rect(page, rect, C_NONE)
    page.draw_rect(rect, color=(0.55, 0.55, 0.55), width=1)
    _centered_text(page, rect, message, 13, color=(0.35, 0.35, 0.35))


def _insert_page_image(out_page, src_page, dest_rect):
    pix = src_page.get_pixmap(dpi=RENDER_DPI, alpha=False)
    out_page.insert_image(dest_rect, pixmap=pix, keep_proportion=True)


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------
def build_comparison_pdf(r_pdf, py_pdf, out_doc):
    r_n  = r_pdf.page_count
    py_n = py_pdf.page_count

    col_w = (PAGE_W - DIVIDER_W) / 2

    for label, r_idx, py_idx, r_lib in PAIRS:
        if r_idx is not None and r_idx >= r_n:
            print(f"  WARNING: R page {r_idx} out of range for '{label}'")
            r_idx = None
        if py_idx is not None and py_idx >= py_n:
            print(f"  WARNING: Python page {py_idx} out of range for '{label}'")
            py_idx = None

        out_page = out_doc.new_page(width=PAGE_W, height=PAGE_H)

        # ── Title banner ─────────────────────────────────────────────────
        hdr = fitz.Rect(0, 0, PAGE_W, HEADER_H)
        _fill_rect(out_page, hdr, C_HEADER_BG)
        _centered_text(out_page, hdr, label, 17, font_name="hebo", color=C_HEADER_FG)

        # ── Sub-header strips ────────────────────────────────────────────
        sub_y0 = HEADER_H
        sub_y1 = HEADER_H + SUBLABEL_H

        lib_color = LIBRARY_COLORS.get(r_lib, C_BASE_R)
        r_sub  = fitz.Rect(0,                   sub_y0, col_w,  sub_y1)
        py_sub = fitz.Rect(col_w + DIVIDER_W,   sub_y0, PAGE_W, sub_y1)

        _fill_rect(out_page, r_sub, lib_color)
        _fill_rect(out_page, py_sub, C_PY)

        r_sub_label  = f"R  |  {r_lib}"
        py_sub_label = "Python  |  matplotlib"
        _centered_text(out_page, r_sub,  r_sub_label,  12, color=(0.1, 0.1, 0.3))
        _centered_text(out_page, py_sub, py_sub_label, 12, color=(0.1, 0.1, 0.3))

        # ── Centre divider ───────────────────────────────────────────────
        out_page.draw_line(
            fitz.Point(col_w, 0), fitz.Point(col_w, PAGE_H),
            color=C_DIVIDER, width=DIVIDER_W
        )

        # ── Annotation strip (bottom of R column) ────────────────────────
        ann_y0 = PAGE_H - ANNOT_H
        ann_y1 = PAGE_H
        ann_rect = fitz.Rect(MARGIN, ann_y0, col_w - MARGIN, ann_y1)

        if r_idx is not None:
            annotations = extract_symbol_annotations(r_pdf[r_idx])
            if annotations:
                unique_ann = list(dict.fromkeys(annotations))   # dedupe, preserve order
                ann_label = "Annotations (Symbol font):  " + "  ".join(unique_ann)
            else:
                ann_label = "Annotations: none detected in text layer"
            _fill_rect(out_page, fitz.Rect(0, ann_y0, col_w, ann_y1), C_ANNOT_BG)
            font = fitz.Font("helv")
            fs = 9
            tw = fitz.TextWriter(out_page.rect)
            tw.append((MARGIN + 4, ann_y0 + ANNOT_H * 0.68),
                      ann_label.encode("ascii", "replace").decode("ascii"),
                      fontsize=fs, font=font)
            tw.write_text(out_page, color=(0.2, 0.45, 0.2))

        # ── Image areas ──────────────────────────────────────────────────
        img_top = sub_y1 + MARGIN
        img_bot = ann_y0 - MARGIN if r_idx is not None else PAGE_H - MARGIN

        r_img  = fitz.Rect(MARGIN,                    img_top, col_w - MARGIN,  img_bot)
        py_img = fitz.Rect(col_w + DIVIDER_W + MARGIN, img_top, PAGE_W - MARGIN, PAGE_H - MARGIN)

        if r_idx is not None:
            _insert_page_image(out_page, r_pdf[r_idx], r_img)
        else:
            _placeholder(out_page, r_img, "Not included in R output")

        if py_idx is not None:
            _insert_page_image(out_page, py_pdf[py_idx], py_img)
        else:
            _placeholder(out_page, py_img, "Not included in Python output")

        safe = label.encode("ascii", "replace").decode("ascii")
        print(f"  OK  {safe}  [{r_lib}]")

    return out_doc


def main():
    print("\n" + "=" * 72)
    print("  Building Ch2 Comparison PDF  (R vs Python, with library labels)")
    print("=" * 72 + "\n")

    for path, name in [(R_PDF_PATH, "R figures PDF"), (PY_PDF_PATH, "Python figures PDF")]:
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"{name} not found:\n  {path}\n"
                "Run the R and Python scripts first to generate the source PDFs."
            )

    r_pdf   = fitz.open(R_PDF_PATH)
    py_pdf  = fitz.open(PY_PDF_PATH)
    out_doc = fitz.open()

    print(f"R PDF:      {r_pdf.page_count} pages")
    print(f"Python PDF: {py_pdf.page_count} pages")
    print(f"Figures:    {len(PAIRS)} pairs\n")
    print("Legend: sub-header colour = R graphics library")
    print("  Blue   = Base R (par/plot/lines/text)")
    print("  Green  = lattice (via PCRA::tsPlotMP)")
    print("  Amber  = ggplot2")
    print("  Violet = xts (plot.xts / addSeries)")
    print("  Wheat  = zoo + Base R (plot.zoo)")
    print()

    build_comparison_pdf(r_pdf, py_pdf, out_doc)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_doc.save(OUT_PATH, garbage=4, deflate=True)
    out_doc.close()
    r_pdf.close()
    py_pdf.close()

    size_kb = os.path.getsize(OUT_PATH) // 1024
    print(f"\nSaved:  {OUT_PATH}")
    print(f"Size:   {size_kb} KB   |   Pages: {len(PAIRS)}")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
