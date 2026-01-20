import logging
import asyncio

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import handlers.transactions as hnd_tr

import database as db
from dotenv import load_dotenv
import os
load_dotenv()

ASKING_NAME = 1
MAKE_TRANSACTIONS = 2

HANDLE_FEEDBACK = 1

HANDLE_TRANSACTION = 1

MAIN_KEYBOARDS = ReplyKeyboardMarkup([
    [KeyboardButton("Yangi yozish")],
    [KeyboardButton("Bugungi hisobot")],
    [KeyboardButton("Feedback")]
], resize_keyboard=True)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Logging sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     await update.message.reply_text(
    #         "Assalomu alaykum!\nQanday xarajatlar qilganingiz va yoki daromadingizni yozing. Men bularni eslab qolib kunlik va haftalik harajatlaringizni hisoblab hisobotlar berib boraman\n\
    # Bu bilan siz xarajatlaringizni kuzatib borasiz.\
    # Shu kabi matn yozsangiz kifoya:\n\n\
    # 1700 bilan atobusda borib keldim. 30mingga tushlik qildim."
    #     )
    user_id = update.effective_user.id
    check_user_exists = await asyncio.to_thread(db.is_user_exists, user_id)
    if not check_user_exists:
        await update.message.reply_text(
            "Salom! 👋\n\nMen men moliyaviy yordamchiman.\nSizga kim deb murojaat qilay?"
        )
        return ASKING_NAME
    else:
        await update.message.reply_text(
            "Salom",
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


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi")
    return ConversationHandler.END

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
    conv_feedback = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex(r'^Feedback$'), start_feedback)],
        states={
            HANDLE_FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    conv_new_transaction = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex(r'^Yangi yozish$'), hnd_tr.start_transaction)],
        states={
            HANDLE_TRANSACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, hnd_tr.handle_transaction)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    logger.info("Bot started")
    application.add_handler(conv_resgister)
    application.add_handler(conv_feedback)
    application.add_handler(conv_new_transaction)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
