import pandas as pd


def analyze_dataframe(df: pd.DataFrame) -> dict:
    """
    بتحلل الـ DataFrame وترجع dict فيه كل الإحصائيات
    """
    report = {}

    # المعلومات الأساسية
    report["rows"] = len(df)
    report["columns"] = len(df.columns)
    report["column_names"] = list(df.columns)

    # الأعمدة الرقمية
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    report["numeric_columns"] = numeric_cols

    # إحصائيات الأعمدة الرقمية
    stats = {}
    for col in numeric_cols:
        stats[col] = {
            "mean":   round(df[col].mean(), 2),
            "median": round(df[col].median(), 2),
            "min":    round(df[col].min(), 2),
            "max":    round(df[col].max(), 2),
            "std":    round(df[col].std(), 2),
        }
    report["stats"] = stats

    return report


def format_analysis_report(report: dict) -> str:
    """
    بتحول الـ report لرسالة نصية منسقة تتبعت للمستخدم
    """
    msg = "📊 *تقرير تحليل البيانات:*\n\n"

    # المعلومات الأساسية
    msg += f"🗂️ عدد الصفوف: *{report['rows']}*\n"
    msg += f"📋 عدد الأعمدة: *{report['columns']}*\n"
    msg += f"🏷️ أسماء الأعمدة: `{', '.join(report['column_names'])}`\n\n"

    # إحصائيات كل عمود رقمي
    if report["stats"]:
        msg += "📈 *الإحصائيات التفصيلية:*\n"
        for col, s in report["stats"].items():
            msg += (
                f"\n🔹 *{col}*\n"
                f"   • المتوسط: {s['mean']}\n"
                f"   • الوسيط: {s['median']}\n"
                f"   • الأدنى: {s['min']}\n"
                f"   • الأعلى: {s['max']}\n"
                f"   • الانحراف المعياري: {s['std']}\n"
            )
    else:
        msg += "⚠️ لا توجد أعمدة رقمية للتحليل."

    return msg