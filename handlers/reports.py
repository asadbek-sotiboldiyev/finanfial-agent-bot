import asyncio
import json
import random as rd
from datetime import datetime

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import database as db
from global_config import cancel

TODAY = 1


async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    date = datetime.now().strftime("%Y-%m-%d")
    transactions = await asyncio.to_thread(db.get_transactions, user_id, date)
    print(transactions)
    total_count = len(transactions)

    total_income = total_expense = count_in = count_out = 0
    for transaction in transactions:
        if transaction[1] == "in":
            total_income += transaction[0]
            count_in += 1
        elif transaction[1] == "out":
            total_expense += transaction[0]
            count_out += 1

    total_net = total_income - total_expense
    await update.message.reply_text(
        f"🗒Bugungi hisobot {date}\n\n"
        f"💰 Kirimlar: {int(total_income):,}\n"
        f"💸 Chiqimlar: {int(total_expense):,}\n"
        f"{('🟢 Net: +' if total_net > 0 else '🔴 Net: -')}{int(total_net):,}\n\n"
        f"📊 {total_count} ta operatsiya ({count_in} ⬇️, {count_out} ⬆️)"
    )


handlers = [
    MessageHandler(
        filters.TEXT & filters.Regex(r"^Bugungi hisobot$"),
        handle_report,
    )
]

# conv_new_transaction = ConversationHandler(
#     entry_points=[
#         MessageHandler(
#             filters.TEXT & filters.Regex(r"^Bugungi hisobot$"),
#             handle_report,
#         )
#     ],
#     states={
#         TODAY: [
#             MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction)
#         ]
#     },
#     fallbacks=[CommandHandler("cancel", cancel)],
# )
