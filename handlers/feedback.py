from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    filters,
)

from dotenv import load_dotenv
import os
load_dotenv()

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
HANDLE_FEEDBACK = 1

async def start_feedback(update: Update, conect: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xizmat bo'yicha fikr-mulohaza, talab va takliflaringizni adminga yozib qoldiring.\nBekor qilish uchun - /cancel",
        reply_markup = ReplyKeyboardRemove()
    )
    return HANDLE_FEEDBACK

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    firstname = update.effective_user.first_name
    username = update.effective_user.username
    await context.bot.send_message(
        chat_id = ADMIN_CHAT_ID,
        text = f"✍️ NEW FEEDBACK\nuser_id: {user_id}\nname: {firstname}\n" + (f"@{username}" if username else "")
    )
    await context.bot.send_message(
        chat_id = ADMIN_CHAT_ID,
        text = f"=== FEEDBACK ===\n{message}"
    )
    await update.message.reply_text("Feedback uchun rahmat!\n Xabaringiz adminga yuborildi", reply_markup=MAIN_KEYBOARDS)
    return ConversationHandler.END

