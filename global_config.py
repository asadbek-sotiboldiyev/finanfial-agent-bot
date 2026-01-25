import os

from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

load_dotenv()

TOKEN = str(os.getenv("BOT_TOKEN"))
ADMIN_CHAT_ID = str(os.getenv("ADMIN_CHAT_ID"))


MAIN_KEYBOARDS = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Yangi harajat")],
        [KeyboardButton("Bugungi hisobot")],
        [KeyboardButton("Feedback")],
    ],
    resize_keyboard=True,
)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi")
    return ConversationHandler.END
