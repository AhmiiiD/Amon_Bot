
import pandas as pd


def clean_dataframe(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """
    Clean a DataFrame and return the cleaned data
    together with a report of the changes.
    """

    # Work on a copy to avoid modifying the original DataFrame
    df = df.copy()

    report = {}

    # 1. Basic validation
    if df.empty:
        raise ValueError("الملف لا يحتوي على بيانات.")

    if len(df.columns) == 0:
        raise ValueError("الملف لا يحتوي على أعمدة.")

    report["rows_before"] = len(df)
    report["columns_count"] = len(df.columns)

    # 2. Remove duplicate rows
    rows_before_dedup = len(df)
    df = df.drop_duplicates().copy()

    report["removed_duplicates"] = (
        rows_before_dedup - len(df)
    )

    # 3. Normalize blank strings to missing values
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    # 4. Count missing values before imputation
    missing_before = int(df.isna().sum().sum())
    report["missing_before"] = missing_before

    # 5. Convert text columns to numeric when safe
    converted_columns = []

    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    for col in text_columns:
        original = df[col]
        non_missing = original.dropna()

        if non_missing.empty:
            continue

        converted = pd.to_numeric(
            original,
            errors="coerce",
        )

        # Convert only if every existing value is numeric
        if converted.loc[non_missing.index].notna().all():
            df[col] = converted
            converted_columns.append(str(col))

    report["converted_columns"] = converted_columns

    # 6. Fill missing numeric values with the mean
    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns.tolist()

    filled_numeric = 0

    for col in numeric_columns:
        missing_count = int(df[col].isna().sum())

        if missing_count == 0:
            continue

        mean_value = df[col].mean()

        # An all-missing or non-finite mean cannot be used
        if pd.notna(mean_value):
            df[col] = df[col].fillna(mean_value)
            filled_numeric += missing_count

    # 7. Fill missing text values with "Unknown"
    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    filled_text = 0

    for col in text_columns:
        missing_count = int(df[col].isna().sum())

        if missing_count:
            df[col] = df[col].fillna("Unknown")
            filled_text += missing_count

    report["filled_numeric"] = filled_numeric
    report["filled_text"] = filled_text

    # 8. Count remaining missing values
    missing_after = int(df.isna().sum().sum())

    report["missing_after"] = missing_after
    report["fixed_missing"] = (
        missing_before - missing_after
    )

    # 9. Final dimensions
    report["rows_after"] = len(df)
    report["columns_after"] = len(df.columns)

    return df, report


def format_cleaning_report(report: dict) -> str:
    """Format the cleaning results as a Telegram message."""

    msg = (
        "🧹 *تقرير تنظيف البيانات*\n\n"
        f"📊 الصفوف قبل التنظيف: {report['rows_before']}\n"
        f"🗑️ الصفوف المكررة المحذوفة: "
        f"{report['removed_duplicates']}\n"
        f"❓ القيم المفقودة قبل المعالجة: "
        f"{report['missing_before']}\n"
        f"✅ القيم التي تمت معالجتها: "
        f"{report['fixed_missing']}\n"
        f"⚠️ القيم المفقودة المتبقية: "
        f"{report['missing_after']}\n"
        f"📐 الصفوف بعد التنظيف: {report['rows_after']}\n"
        f"📋 عدد الأعمدة: {report['columns_after']}\n"
    )

    if report["converted_columns"]:
        columns = ", ".join(report["converted_columns"])
        msg += f"\n🔄 الأعمدة المحوّلة لأرقام: {columns}"

    if report["missing_after"] > 0:
        msg += (
            "\n\n⚠️ بعض القيم المفقودة لم تُعالج "
            "لأن تحديد قيمة بديلة لها يحتاج قرارًا مناسبًا."
        )

    return msg
