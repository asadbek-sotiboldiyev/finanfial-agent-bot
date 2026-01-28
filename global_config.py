import os

from dotenv import load_dotenv
from telegram import Bot, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

load_dotenv()

TOKEN = str(os.getenv("BOT_TOKEN"))
ADMIN_CHAT_ID = str(os.getenv("ADMIN_CHAT_ID"))
WEBHOOK_PATH = "/webhook"
APP_URL = str(os.getenv("APP_URL"))
PORT = 8000


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


async def send_message_to_admin(message: str):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
