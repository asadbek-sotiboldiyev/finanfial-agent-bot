from email import message

from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import database_pgsql as db
from global_config import (
    ADMIN_CHAT_ID,
    cancel,
    get_main_keyboards,
    send_message_to_user,
)

GOTO_PANEL, SEND_MESSAGE_TO_USERS = range(2)
PANEL_KEYBOARDS = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Statistika")],
        [KeyboardButton("MessageToAll")],
        [KeyboardButton("Chiqish")],
    ],
    resize_keyboard=True,
)


async def get_statistic():
    user_count, raw_message_count, transaction_count = await db.get_basic_stats()
    text = f"👤Foydalanuvchilar soni: {user_count}\n✏️Yuborilgan xabarlar: {raw_message_count}\n💾Umumiy yozilgan tranzaksiyalar: {transaction_count}"
    return text


async def goto_adminpanel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        await update.message.reply_text(
            "Siz admin paneliga kirish uchun ruxsat yo'q",
            reply_markup=await get_main_keyboards(user_id),
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "Admin paneliga xush kelibsiz!",
        reply_markup=PANEL_KEYBOARDS,
    )
    return GOTO_PANEL


async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        await update.message.reply_text(
            "Siz admin paneliga kirish uchun ruxsat yo'q",
            reply_markup=await get_main_keyboards(user_id),
        )
        return ConversationHandler.END

    message = update.message.text
    if message == "Statistika":
        stats = await get_statistic()
        current_datetime = update.message.date.strftime("%Y-%m-%d %H:%M")
        text = f"📆 {current_datetime} Statistika:\n\n{stats}"
        await update.message.reply_text(
            text,
            reply_markup=PANEL_KEYBOARDS,
        )
    if message == "MessageToAll":
        await update.message.reply_text(
            "Xabar matnini kiriting:",
            reply_markup=PANEL_KEYBOARDS,
        )
        return SEND_MESSAGE_TO_USERS
    if message == "Chiqish":
        await update.message.reply_text(
            "Asosiy sahifa",
            reply_markup=await get_main_keyboards(user_id),
        )
    return GOTO_PANEL


async def send_message_to_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    users = await db.get_users_ids()
    for user in users:
        await send_message_to_user(user, message)
    await update.message.reply_text(
        "Xabar yuborildi!",
        reply_markup=PANEL_KEYBOARDS,
    )
    return GOTO_PANEL


conv_admin = ConversationHandler(
    entry_points=[
        MessageHandler(filters.TEXT & filters.Regex(r"^Adminpanel$"), goto_adminpanel)
    ],
    states={
        GOTO_PANEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin)],
        SEND_MESSAGE_TO_USERS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, send_message_to_users)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
