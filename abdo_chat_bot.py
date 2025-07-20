from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8120876505:AAG1OJbhN0c6JXlWJSEZwIJRoP_gl32K92k"

ASK_USERNAME, ASK_REASON, ASK_COUNT = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل اسم المستخدم المستهدف (إنستغرام):")
    return ASK_USERNAME

async def ask_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("حدد نوع البلاغ:\n1- تحرش\n2- ابتزاز\n3- عنف")
    return ASK_REASON

async def ask_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reasons = {'1': 'تحرش', '2': 'ابتزاز', '3': 'عنف'}
    user_reason = update.message.text.strip()
    context.user_data['reason'] = reasons.get(user_reason, 'غير معروف')
    await update.message.reply_text("كم عدد البلاغات التي تريد تنفيذها؟ (رقم)")
    return ASK_COUNT

async def report_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data['username']
    reason = context.user_data['reason']
    count = update.message.text.strip()
    msg = f"✅ تم تسجيل {count} بلاغ على @{username} بسبب: {reason}!"
    await update.message.reply_text(msg)
    # سجل البلاغ في ملف نصي
    with open("bot_reports.txt", "a", encoding="utf-8") as f:
        f.write(f"{username} - {reason} - {count} @ {update.effective_user.username}\n")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.")
    return ConversationHandler.END

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_reason)],
            ASK_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_count)],
            ASK_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_done)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    app.run_polling()