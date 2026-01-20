import asyncio
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
HANDLE_TRANSACTION = 1
async def start_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xarajatlar yoki daromadingizni shu kabi matn yozsangiz:\n>1700 bilan atobusda borib keldim\. 30mingga tushlik qildim",
        parse_mode="MarkdownV2"
    )
    return 1

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    message = update.message.text
    await update.message.reply_text("Saqlanyabdi...")
    await asyncio.sleep(3)
    # save_message -> AI -> save_ai_extract -> save_transaction -> return to user
    await context.bot.delete_message(chat_id=chat_id, message_id=int(message_id)+1)
    await update.message.reply_text("Saqlandi")
    return ConversationHandler.END


