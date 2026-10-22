import os
import uuid
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.cleaner import clean_dataframe, format_cleaning_report
from handlers.analyzer import analyze_dataframe, format_analysis_report
from handlers.charter import generate_chart
from handlers.pdf_generator import generate_pdf
from database import save_analysis          # ← جديد

TMP_DIR = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls"]
user_data_store = {}


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    document = message.document

    if not document:
        await message.reply_text("❌ من فضلك أرسل ملف CSV أو Excel فقط.")
        return

    file_name = document.file_name
    _, ext = os.path.splitext(file_name.lower())

    if ext not in ALLOWED_EXTENSIONS:
        await message.reply_text(
            f"❌ نوع الملف '{ext}' غير مدعوم.\n"
            "✅ الأنواع المدعومة: CSV, XLSX, XLS فقط."
        )
        return

    await message.reply_text("📥 جاري استلام الملف...")

    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(TMP_DIR, unique_name)
    file = await context.bot.get_file(document.file_id)
    await file.download_to_drive(file_path)

    try:
        if ext == ".csv":
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin-1")
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        await message.reply_text(f"❌ حصل خطأ في قراءة الملف:\n{str(e)}")
        os.remove(file_path)
        return

    df_clean, cleaning_report = clean_dataframe(df)
    await message.reply_text(
        format_cleaning_report(cleaning_report), parse_mode="Markdown"
    )

    analysis_report = analyze_dataframe(df_clean)
    await message.reply_text(
        format_analysis_report(analysis_report), parse_mode="Markdown"
    )

    user_id = update.effective_user.id
    user_data_store[user_id] = {
        "df":              df_clean,
        "cleaning_report": cleaning_report,
        "analysis_report": analysis_report,
        "file_name":       file_name,
        "username":        update.effective_user.username or "unknown",
    }

    keyboard = [
        [
            InlineKeyboardButton("📊 Bar Chart",  callback_data="chart_bar"),
            InlineKeyboardButton("📈 Line Chart", callback_data="chart_line"),
        ],
        [
            InlineKeyboardButton("🥧 Pie Chart",  callback_data="chart_pie"),
            InlineKeyboardButton("🌡️ Heatmap",   callback_data="chart_heatmap"),
        ],
    ]
    await message.reply_text(
        "📉 اختار نوع الـ Chart اللي عايزه:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    os.remove(file_path)


async def handle_chart_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    chart_type = query.data.replace("chart_", "")

    data = user_data_store.get(user_id)
    if data is None:
        await query.message.reply_text("❌ انتهت صلاحية البيانات، من فضلك أرسل الملف مجدداً.")
        return

    await query.message.reply_text("🎨 جاري رسم الـ Chart وتوليد التقرير...")

    try:
        chart_buf = generate_chart(data["df"], chart_type)

        chart_buf.seek(0)
        await query.message.reply_photo(
            photo=chart_buf,
            caption=f"✅ {chart_type.capitalize()} Chart جاهز!"
        )

        chart_buf.seek(0)
        pdf_buf = generate_pdf(
            cleaning_report=data["cleaning_report"],
            analysis_report=data["analysis_report"],
            chart_buf=chart_buf,
            file_name=data["file_name"],
        )

        await query.message.reply_document(
            document=pdf_buf,
            filename="analysis_report.pdf",
            caption="📄 تقرير التحليل الكامل جاهز!"
        )

        # ← حفظ التحليل في قاعدة البيانات
        save_analysis(
            user_id=user_id,
            username=data["username"],
            file_name=data["file_name"],
            rows=data["analysis_report"]["rows"],
            columns=data["analysis_report"]["columns"],
            chart_type=chart_type,
        )

    except ValueError as e:
        await query.message.reply_text(f"❌ {str(e)}")
    except Exception as e:
        await query.message.reply_text(f"❌ حصل خطأ:\n{str(e)}")