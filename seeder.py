import json
import random as rd

from database import (
    init_database,
    save_extracted_data,
    save_message,
    save_transactions,
    save_user,
)
from global_config import ADMIN_CHAT_ID

# Users seed
users = [
    {
        "user_id": ADMIN_CHAT_ID,
        "firstname": "CEO",
        "original_name": "Asadbek Sotiboldiyev",
        "username": "asadbek_sotiboldiyev",
    },
    {
        "user_id": 123,
        "firstname": "John",
        "original_name": "John Doe",
        "username": "johndoe",
    },
    {
        "user_id": 456,
        "firstname": "Jane",
        "original_name": "Jane Smith",
        "username": "janesmith",
    },
    {
        "user_id": 789,
        "firstname": "Alice",
        "original_name": "Alice Johnson",
        "username": "alicejohnson",
    },
]

# Raw messages and extracted datas
data = []
for i in range(100):
    data.append(
        {
            "user_id": rd.choice(users)["user_id"],
            "tg_message_id": rd.randint(1000, 9999),
            "raw_message": f"Hello, {rd.choice(users)['firstname']}!",
            "sent_time": f"2026-01-{rd.randint(1, 31):02d} {rd.randint(0, 23):02d}:{rd.randint(0, 59):02d}:05+00:00",
        }
    )


# Initialize database
init_database()

# Save users
for user in users:
    save_user(
        user_id=user["user_id"],
        firstname=user["firstname"],
        original_name=user["original_name"],
        username=user["username"],
    )
    print(f"User {user['firstname']} saved")

# Save messages
for index, message in enumerate(data):
    print(f"--------{index + 1}-Message-----------")
    user_id = message["user_id"]
    message_row_id = save_message(
        user_id=user_id,
        tg_message_id=message["tg_message_id"],
        message=message["raw_message"],
        sent_time=message["sent_time"],
    )
    print(f"Message {message['user_id']}|{message['tg_message_id']} saved")

    # Fake transaction for message
    random_cnt = rd.randint(1, 5)
    random_data = []
    for i in range(random_cnt):
        random_data.append(
            json.dumps(
                {
                    "amount": rd.randint(1, 500) * 1000,
                    "description": f"random_{i}",
                    "type": rd.choice(["in", "out"]),
                }
            )
        )
    text = "[" + ",".join(random_data) + "]"
    transactions = json.loads(text)
    row_id = save_extracted_data(message_row_id, text)
    print("Extracted data saved")
    save_transactions(transactions, user_id, row_id, date=message["sent_time"][:10])
    print(f"{random_cnt} transactions saved")
