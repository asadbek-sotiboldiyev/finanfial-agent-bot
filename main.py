import logging
from contextlib import asynccontextmanager

import pytz
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    Defaults,
    MessageHandler,
    filters,
)

import database_async as db
import handlers.adminpanel as hnd_ad
import handlers.feedback as hnd_fd
import handlers.reports as hnd_rp
import handlers.transactions as hnd_tr
from global_config import (
    APP_URL,
    PORT,
    TOKEN,
    WEBHOOK_PATH,
    get_main_keyboards,
    send_message_to_admin,
)

load_dotenv()

ASKING_NAME = 1


# Logging sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
application: Application | None = None


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Botdan foydalanish uchunqo'llanma.\n\n"
        "1. /start - Botni ishga tushirish\n"
        "2. /help - Yordam\n"
        "3. /cancel- Hozirgi amalni bekor qilish\n"
        "Panel:\n"
        "1. Yangi harajat qo'shish\n"
        "2. Bugungi hisobotni olish\n"
        "3. Admin ga fikr va murojaatingizni yuborish\n"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    check_user_exists = await db.is_user_exists(user_id)
    if not check_user_exists:
        await update.message.reply_text(
            "Salom! 👋\n\nMen men moliyaviy yordamchiman.\nSizga kim deb murojaat qilay?"
        )
        return ASKING_NAME
    else:
        name = check_user_exists[0]
        await update.message.reply_text(
            f"Salom, {name}!\nQuyidagi panel orqali botdan foydalaning",
            reply_markup=await get_main_keyboards(user_id),
        )
        return ConversationHandler.END


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save user's first name"""
    user_id = update.effective_user.id
    firstname = update.message.text.strip()
    original_name = update.message.from_user.full_name
    username = update.message.from_user.username

    await db.save_user(user_id, firstname, original_name, username)

    await update.message.reply_text(
        f"Tanishganimdan hursandman, {firstname}! 😊\n\n"
        "Xaridlar, xarajat va daromadlaringizni ayting. Men buni siz uchun saqlab boraman va hisobotlar berib boraman.\n"
        "Feedback tugmasi orqali adminga fikrlaringiz va tavsiyalaringizni yuborish yuborishingiz mumkin.",
        reply_markup=await get_main_keyboards(user_id),
    )

    # TODO: send notification to admin
    await send_message_to_admin(
        f"New user registered: <b>{original_name}</b> - ({firstname})\nuser_id: <pre>{user_id}</pre>\nusername: @{username}",
        parse_mode="HTML",
    )

    return ConversationHandler.END


@asynccontextmanager
async def lifespan(app: FastAPI):
    global application
    timezone_uz = pytz.timezone("Asia/Tashkent")
    defaults = Defaults(tzinfo=timezone_uz)
    application = Application.builder().token(TOKEN).defaults(defaults).build()
    await db.init_database()

    conv_resgister = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASKING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    logger.info("Bot started")
    application.add_handler(conv_resgister)
    application.add_handler(CommandHandler("help", help))
    application.add_handlers(hnd_rp.handlers)
    application.add_handler(hnd_fd.conv_feedback)
    application.add_handler(hnd_tr.conv_new_transaction)
    application.add_handler(hnd_ad.conv_admin)

    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=APP_URL + WEBHOOK_PATH)
    print("Webhook set to:", APP_URL + WEBHOOK_PATH)

    yield
    # Shutdown

    print("Shutting down...")
    if application:
        await application.stop()
        await application.shutdown()


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def webhook_handler(request: Request):
    """Handle webhook requests"""
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
    return Response(status_code=200)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
    }


@app.post("/set-webhook")
async def set_webhook():
    """Manually set the webhook (useful for testing)"""
    try:
        await application.bot.set_webhook(url=APP_URL)
        return {"status": "success", "webhook_url": APP_URL}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.delete("/webhook")
async def delete_webhook():
    """Delete the webhook"""
    try:
        await application.bot.delete_webhook()
        return {"status": "webhook deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
    )
