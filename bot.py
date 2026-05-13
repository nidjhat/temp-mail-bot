

import requests
import random
import string
import nest_asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

nest_asyncio.apply()

BOT_TOKEN = "8770001757:AAGacSimXqe3nc1EUZX64hMJ3TwCuVKJWD8"

BASE = "https://api.mail.tm"

users = {}

def random_name():
    return ''.join(random.choices(string.ascii_lowercase, k=10))

def create_mail():

    domains = requests.get(f"{BASE}/domains").json()

    domain = domains['hydra:member'][0]['domain']

    email = f"{random_name()}@{domain}"

    password = "pass123456"

    requests.post(
        f"{BASE}/accounts",
        json={
            "address": email,
            "password": password
        }
    )

    token_res = requests.post(
        f"{BASE}/token",
        json={
            "address": email,
            "password": password
        }
    ).json()

    return email, token_res['token']

def get_messages(token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(
        f"{BASE}/messages",
        headers=headers
    )

    return r.json()

def get_message_content(token, msg_id):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(
        f"{BASE}/messages/{msg_id}",
        headers=headers
    )

    return r.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [

        [InlineKeyboardButton(
            "📺 Open YouTube Channel",
            callback_data="open_channel"
        )],

        [InlineKeyboardButton(
            "✅ I Subscribed",
            callback_data="subscribed"
        )]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔥 Subscribe to continue",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if query.data == "open_channel":

        users[user_id] = "opened"

        await query.message.reply_text(
            "📺 Open this channel:\n\nhttps://www.youtube.com/@nidjhat\n\nThen click 'I Subscribed'"
        )

    elif query.data == "subscribed":

        if users.get(user_id) != "opened":

            await query.message.reply_text(
                "❌ First click 'Open YouTube Channel'"
            )

            return

        users[user_id] = "subscribed"

        keyboard = [

            [InlineKeyboardButton(
                "📧 Create Mail",
                callback_data="newmail"
            )],

            [InlineKeyboardButton(
                "📥 Inbox",
                callback_data="inbox"
            )],

            [InlineKeyboardButton(
                "🗑 Delete Mail",
                callback_data="delete"
            )],

            [InlineKeyboardButton(
                "🔄 Refresh Inbox",
                callback_data="refresh"
            )]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            "✅ Access Granted",
            reply_markup=reply_markup
        )

    elif query.data == "newmail":

        if users.get(user_id) != "subscribed":

            await query.message.reply_text(
                "❌ Subscribe first"
            )

            return

        email, token = create_mail()

        users[f"{user_id}_mail"] = token

        await query.message.reply_text(
            f"📧 Your Temp Mail:\n\n{email}"
        )

    elif query.data == "inbox" or query.data == "refresh":

        token = users.get(f"{user_id}_mail")

        if not token:

            await query.message.reply_text(
                "❌ Create a mail first"
            )

            return

        msgs = get_messages(token)

        if msgs['hydra:totalItems'] == 0:

            await query.message.reply_text(
                "📭 Inbox Empty"
            )

            return

        result = "📨 Inbox Messages:\n\n"

        for msg in msgs['hydra:member']:

            full_msg = get_message_content(
                token,
                msg['id']
            )

            result += f"📩 From: {msg['from']['address']}\n"

            result += f"📝 Subject: {msg['subject']}\n\n"

            if 'text' in full_msg:

                result += f"{full_msg['text']}\n\n"

            result += "----------------------\n\n"

        await query.message.reply_text(result[:4000])

    elif query.data == "delete":

        if f"{user_id}_mail" in users:

            del users[f"{user_id}_mail"]

        await query.message.reply_text(
            "🗑 Mail Deleted"
        )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CallbackQueryHandler(button))

print("BOT STARTED")

app.run_polling()
