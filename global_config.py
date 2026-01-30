import os

from dotenv import load_dotenv
from telegram import Bot, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

load_dotenv()

TOKEN = str(os.getenv("BOT_TOKEN"))
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
WEBHOOK_PATH = "/webhook"
APP_URL = str(os.getenv("APP_URL"))
PORT = int(os.getenv("PORT"))


MAIN_KEYBOARDS = [
    [KeyboardButton("Yangi harajat")],
    [KeyboardButton("Bugungi hisobot")],
    [KeyboardButton("Feedback")],
]


async def get_main_keyboards(user_id):
    global MAIN_KEYBOARDS
    if user_id == ADMIN_CHAT_ID:
        MAIN_KEYBOARDS = [
            [KeyboardButton("Yangi harajat")],
            [KeyboardButton("Bugungi hisobot")],
            [KeyboardButton("Adminpanel")],
        ]
    return ReplyKeyboardMarkup(
        MAIN_KEYBOARDS,
        resize_keyboard=True,
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bekor qilindi",
        reply_markup=await get_main_keyboards(update.message.from_user.id),
    )
    return ConversationHandler.END


async def send_message_to_admin(message: str, **kwargs):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, **kwargs)


async def send_message_to_user(user_id, message, **kwargs):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=user_id, text=message, **kwargs)
