import io
import tempfile
import os
from fpdf import FPDF


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(41, 128, 185)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "Data Analysis Report", align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_pdf(
    cleaning_report: dict,
    analysis_report: dict,
    chart_buf: io.BytesIO,
    file_name: str = "report"
) -> io.BytesIO:
    """
    بتولد PDF فيه:
    - تقرير الـ Cleaning
    - تقرير التحليل الإحصائي
    - صورة الـ Chart
    وبترجع الـ PDF كـ BytesIO جاهز للإرسال
    """

    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Section 1: Cleaning Report ──────────────────────────
    _section_title(pdf, "1. Data Cleaning Report")

    _key_value(pdf, "Duplicate rows removed", str(cleaning_report["removed_duplicates"]))
    _key_value(pdf, "Missing values fixed",   str(cleaning_report["fixed_missing"]))
    _key_value(pdf, "Rows after cleaning",    str(cleaning_report["rows_after"]))

    if cleaning_report.get("converted_columns"):
        cols = ", ".join(cleaning_report["converted_columns"])
        _key_value(pdf, "Columns converted to numeric", cols)

    pdf.ln(6)

    # ── Section 2: Analysis Report ───────────────────────────
    _section_title(pdf, "2. Statistical Analysis")

    _key_value(pdf, "Total rows",    str(analysis_report["rows"]))
    _key_value(pdf, "Total columns", str(analysis_report["columns"]))
    _key_value(pdf, "Column names",  ", ".join(analysis_report["column_names"]))

    pdf.ln(4)

    for col, stats in analysis_report["stats"].items():
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(41, 128, 185)
        pdf.cell(0, 7, f"Column: {col}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

        _key_value(pdf, "  Mean",               str(stats["mean"]))
        _key_value(pdf, "  Median",             str(stats["median"]))
        _key_value(pdf, "  Min",                str(stats["min"]))
        _key_value(pdf, "  Max",                str(stats["max"]))
        _key_value(pdf, "  Std Deviation",      str(stats["std"]))
        pdf.ln(3)

    # ── Section 3: Chart ─────────────────────────────────────
    _section_title(pdf, "3. Chart")

    # الـ fpdf2 محتاج ملف حقيقي مش BytesIO، فبنحفظه مؤقتاً
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
        tmp_img.write(chart_buf.getvalue())
        tmp_img_path = tmp_img.name

    try:
        # لو الصورة هتتجاوز الصفحة، ابدأ صفحة جديدة
        if pdf.get_y() > 180:
            pdf.add_page()

        pdf.image(tmp_img_path, x=15, w=180)
    finally:
        os.remove(tmp_img_path)

    # ── تحويل الـ PDF لـ BytesIO ──────────────────────────────
    pdf_bytes = pdf.output()
    pdf_buf = io.BytesIO(bytes(pdf_bytes))
    pdf_buf.seek(0)

    return pdf_buf


# ── Helper Functions ──────────────────────────────────────────

def _section_title(pdf: FPDF, title: str):
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(236, 240, 241)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 9, title, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _key_value(pdf: FPDF, key: str, value: str):
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(70, 6, f"{key}:", new_x="END", new_y="LAST")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")