import asyncio
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import database as db
import handlers.feedback as hnd_fd
import handlers.transactions as hnd_tr
from global_config import MAIN_KEYBOARDS, TOKEN

load_dotenv()

ASKING_NAME = 1


# Logging sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    check_user_exists = await asyncio.to_thread(db.is_user_exists, user_id)
    if not check_user_exists:
        await update.message.reply_text(
            "Salom! 👋\n\nMen men moliyaviy yordamchiman.\nSizga kim deb murojaat qilay?"
        )
        return ASKING_NAME
    else:
        name = check_user_exists[0]
        await update.message.reply_text(
            f"Salom, {name}!\nQuyidagi panel orqali botdan foydalaning",
            reply_markup=MAIN_KEYBOARDS,
        )
        return ConversationHandler.END


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save user's first name"""
    user_id = update.effective_user.id
    firstname = update.message.text.strip()
    original_name = update.message.from_user.full_name
    username = update.message.from_user.username

    await asyncio.to_thread(db.save_user, user_id, firstname, original_name, username)

    await update.message.reply_text(
        f"Tanishganimdan hursandman, {firstname}! 😊\n\n"
        "Xaridlar, xarajat va daromadlaringizni ayting. Men buni siz uchun saqlab boraman va hisobotlar berib boraman.\n"
        "Feedback tugmasi orqali adminga fikrlaringiz va tavsiyalaringizni yuborish yuborishingiz mumkin.",
        reply_markup=MAIN_KEYBOARDS,
    )

    return ConversationHandler.END


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save user's transactions"""
    # chat_id = update.effective_user.id
    # message = update.message.text
    # sent_time = update.message.date
    # await update.message.reply_text(f'yuborilgan vaqt: {sent_time}')

    # db.save_transaction(chat_id, transaction)

    # await update.message.reply_text(
    #     f"Xaridlar, xarajat va daromadlaringizni ayting. Men buni siz uchun saqlab boraman va hisobotlar berib boraman.\n"
    #     "Feedback tugmasi orqali adminga fikrlaringiz va tavsiyalaringizni yuborish yuborishingiz mumkin.",
    #     reply_markup=reply_markup,
    # )


def main():
    application = Application.builder().token(TOKEN).build()
    db.init_database()

    conv_resgister = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASKING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    logger.info("Bot started")
    application.add_handler(conv_resgister)
    application.add_handler(hnd_fd.conv_feedback)
    application.add_handler(hnd_tr.conv_new_transaction)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
