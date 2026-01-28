import asyncio
import json

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import database as db
from agent import Agent
from global_config import MAIN_KEYBOARDS, cancel, send_message_to_admin

HANDLE_TRANSACTION = 1


async def extract_and_save(user_id, raw_message_id, message):
    # TODO: add messsage to MessageQueue for processing
    text = Agent().ask(message)
    # text = """[{"amount": 18000,"description": "ovqatlanish","type": "out"},{"amount": 12000,"description": "sharbat","type": "out"}]"""  # example for testing

    row_id = await asyncio.to_thread(db.save_extracted_data, raw_message_id, text)
    completed = False
    try:
        transactions = json.loads(text)
    except json.JSONDecodeError as e:
        print(e)
        print(
            f"AI returned non JSON: extracted_data_id: {row_id} | raw_message_id: {raw_message_id}"
        )
        await send_message_to_admin(
            f"AI returned non JSON ⚠️\n\nextracted_data_id: <pre>{row_id}</pre>\nraw_message_id: <pre>{raw_message_id}</pre>"
        )

        return completed, []

    await asyncio.to_thread(
        db.save_transactions,
        transactions,
        user_id,
        row_id,
    )
    completed = True
    return completed, transactions


async def start_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xarajatlar yoki daromadingizni shu kabi matn yozing:\n>1700 bilan atobusda borib keldim\\. 30mingga tushlik qildim",
        parse_mode="MarkdownV2",
        reply_markup=ReplyKeyboardRemove(),
    )
    return HANDLE_TRANSACTION


async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.id
    message = update.message.text
    sent_time = update.message.date

    await update.message.reply_text("Saqlanyabdi...")

    # save_message -> AI -> save_ai_extract -> save_transaction -> return to user

    raw_message_id = await asyncio.to_thread(
        db.save_message, chat_id, message_id, message, sent_time
    )
    is_completed, transactions = await extract_and_save(
        chat_id, raw_message_id, message
    )
    if not is_completed:
        await update.message.reply_text("Xatolik yuz berdi")
        return ConversationHandler.END
    elif is_completed and transactions == []:
        await update.message.reply_text("So'rovingizdan ma'lumotlar topilmadi")
        return ConversationHandler.END
    text_transactioins = []
    for transaction in transactions:
        text_transactioins.append(
            ("↗️ " if transaction["type"] == "out" else "↙️ ")
            + format(transaction["amount"], ",")
            + " <b>"
            + transaction["description"]
            + "</b>"
        )
    print("✅ Saqlandi\n\n" + "\n".join(text_transactioins))
    await context.bot.delete_message(chat_id=chat_id, message_id=int(message_id) + 1)
    await update.message.reply_text(
        "✅ Saqlandi\n\n" + "\n".join(text_transactioins),
        reply_markup=MAIN_KEYBOARDS,
        parse_mode="HTML",
    )
    return ConversationHandler.END


conv_new_transaction = ConversationHandler(
    entry_points=[
        MessageHandler(
            filters.TEXT & filters.Regex(r"^Yangi harajat$"),
            start_transaction,
        )
    ],
    states={
        HANDLE_TRANSACTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
