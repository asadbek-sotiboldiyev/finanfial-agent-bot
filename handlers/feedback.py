from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from global_config import ADMIN_CHAT_ID, cancel, get_main_keyboards

HANDLE_FEEDBACK = 1


async def start_feedback(update: Update, conect: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xizmat bo'yicha fikr-mulohaza, talab va takliflaringizni adminga yozib qoldiring.\nBekor qilish uchun - /cancel",
        reply_markup=ReplyKeyboardRemove(),
    )
    return HANDLE_FEEDBACK


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    firstname = update.effective_user.first_name
    username = update.effective_user.username
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"✍️ NEW FEEDBACK\nuser_id: {user_id}\nname: {firstname}\n"
        + (f"@{username}" if username else ""),
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID, text=f"=== FEEDBACK ===\n{message}"
    )
    await update.message.reply_text(
        "Feedback uchun rahmat!\n Xabaringiz adminga yuborildi",
        reply_markup=await get_main_keyboards(user_id),
    )
    return ConversationHandler.END


conv_feedback = ConversationHandler(
    entry_points=[
        MessageHandler(filters.TEXT & filters.Regex(r"^Feedback$"), start_feedback)
    ],
    states={
        HANDLE_FEEDBACK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
