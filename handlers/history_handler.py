import os
from telegram import Update
from telegram.ext import ContextTypes
from database import get_user_history, get_admin_stats

ADMIN_ID = int(os.getenv("ADMIN_ID", 0))


async def handle_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/history - بيعرض آخر 5 تحليلات للمستخدم"""
    user_id = update.effective_user.id
    records = get_user_history(user_id)

    if not records:
        await update.message.reply_text(
            "📭 مفيش تحليلات سابقة.\n"
            "📂 ابعت ملف CSV أو Excel وأنا هحلله لك!"
        )
        return

    msg = "🕓 *آخر 5 تحليلات:*\n\n"
    for i, rec in enumerate(records, 1):
        date_str = rec["created_at"].strftime("%Y-%m-%d %H:%M")
        msg += (
            f"*{i}.* 📄 `{rec['file_name']}`\n"
            f"   • الصفوف: {rec['rows']} | الأعمدة: {rec['columns']}\n"
            f"   • Chart: {rec['chart_type']}\n"
            f"   • التاريخ: {date_str}\n\n"
        )

    await update.message.reply_text(msg, parse_mode="Markdown")


async def handle_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/stats - للـ Admin فقط"""
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ هذا الأمر متاح للـ Admin فقط.")
        return

    stats = get_admin_stats()

    msg = "📊 *إحصائيات البوت:*\n\n"
    msg += f"👥 إجمالي المستخدمين: *{stats['total_users']}*\n"
    msg += f"📁 إجمالي التحليلات: *{stats['total_analyses']}*\n\n"

    if stats["chart_stats"]:
        msg += "🎨 *أكثر الـ Charts استخداماً:*\n"
        for row in stats["chart_stats"]:
            msg += f"   • {row['chart_type']}: {row['count']} مرة\n"

    await update.message.reply_text(msg, parse_mode="Markdown")