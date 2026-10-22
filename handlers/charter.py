import io
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # بيمنع matplotlib من فتح نافذة
import matplotlib.pyplot as plt
import seaborn as sns


def get_clean_numeric_cols(df: pd.DataFrame) -> list:
    """
    دالة ذكية لاستخراج الأعمدة الرقمية الحقيقية مع استبعاد أعمدة الـ ID والرموز التعريفية
    """
    all_numeric = df.select_dtypes(include="number").columns.tolist()
    
    # استبعاد أي عمود بيعبر عن ID أو Index
    bad_keywords = ['id', 'code', 'index', 'unnamed', 'no', 'number']
    clean_cols = [
        col for col in all_numeric 
        if not any(keyword in col.lower() for keyword in bad_keywords)
    ]
    
    return clean_cols if clean_cols else all_numeric


def generate_chart(df: pd.DataFrame, chart_type: str, target_col: str = None) -> io.BytesIO:
    """
    بترسم الـ Chart المطلوب للعمود المحدد وترجعه كـ BytesIO جاهز للإرسال
    """
    numeric_cols = get_clean_numeric_cols(df)

    if not numeric_cols:
        raise ValueError("لا توجد أعمدة رقمية مناسبة للرسم.")

    # لو لم يتم تحديد عمود، نختار أول عمود نظيف افتراضياً
    if not target_col or target_col not in df.columns:
        target_col = numeric_cols[0]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    if chart_type == "bar":
        # رسم القيم للعمود المحدد
        top_data = df[target_col].dropna().head(15)
        sns.barplot(x=top_data.index, y=top_data.values, ax=ax, palette="viridis")
        ax.set_title(f"Bar Chart - {target_col}", fontsize=14, fontweight='bold')
        ax.set_xlabel("Index", fontsize=11)
        ax.set_ylabel(target_col, fontsize=11)
        plt.xticks(rotation=30, ha='right')

    elif chart_type == "line":
        # رسم الخطوط للعمود المحدد
        data_to_plot = df[target_col].dropna().head(50)
        ax.plot(data_to_plot.values, marker='o', color='b', linewidth=2)
        ax.set_title(f"Line Chart - {target_col}", fontsize=14, fontweight='bold')
        ax.set_xlabel("الصفوف", fontsize=11)
        ax.set_ylabel(target_col, fontsize=11)

    elif chart_type == "pie":
        # رسم الـ Pie للعمود المحدد بناءً على التكرار أو القيم
        val_counts = df[target_col].dropna().value_counts().head(6)
        if len(val_counts) <= 1:
            val_counts = df[target_col].dropna().head(5)
        
        val_counts.plot(
            kind="pie", 
            ax=ax, 
            autopct="%1.1f%%", 
            startangle=140, 
            colors=sns.color_palette("Set2")
        )
        ax.set_title(f"Pie Chart - توزيع: {target_col}", fontsize=14, fontweight='bold')
        ax.set_ylabel("")

    elif chart_type == "heatmap":
        if len(numeric_cols) < 2:
            raise ValueError("الـ Heatmap محتاج عمودين رقميين على الأقل.")
        
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax, linewidths=0.5)
        ax.set_title("Heatmap - مصفوفة الارتباط", fontsize=14, fontweight='bold')

    else:
        raise ValueError(f"نوع الـ Chart '{chart_type}' غير معروف.")

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150)
    buf.seek(0)
    plt.close(fig)

    return buf