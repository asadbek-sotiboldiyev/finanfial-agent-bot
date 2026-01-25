import asyncio
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
import database as db
import json

HANDLE_TRANSACTION = 1

async def work(user_id, raw_message_id, message):
    # text = Agent.ask(message)
    text = """[{"amount": 1700,"description": "avtobus","type": "out"},{"amount": 30000,"description": "ovqatlanish","type": "out"},{"amount": 150000,"description": "naushnik","type": "out"}]""" # example for testing
    transactions = json.loads(text)
    row_id = await asyncio.to_thread(db.save_extracted_transactions, raw_message_id, message)
    await asyncio.to_thread(
        db.save_transactions,
        transactions,
        user_id,
        row_id,
    )
    return True

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
    sent_time = update.message.date

    await update.message.reply_text("Saqlanyabdi...")

    # await asyncio.sleep(3)
    # save_message -> AI -> save_ai_extract -> save_transaction -> return to user

    raw_message_id = await asyncio.to_thread(db.save_message, chat_id, message_id, message, sent_time)
    await work(chat_id, raw_message_id, message)

    await context.bot.delete_message(chat_id=chat_id, message_id=int(message_id)+1)
    await update.message.reply_text("Saqlandi")
    return ConversationHandler.END


