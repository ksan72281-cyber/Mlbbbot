import os
import re
import json
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = TeleBot(BOT_TOKEN)

# Data file သိမ်းဖို့
DATA_FILE = "orders.json"

def load_orders():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_orders(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def is_mlbb_format(text):
    pattern = r'^\d+\(\d+\)[Dd][Ii][Aa]\d+$'
    return bool(re.match(pattern, text.strip()))

def make_keyboard(text):
    markup = InlineKeyboardMarkup()
    copy_btn = InlineKeyboardButton(
        "📋 Copy", 
        callback_data=f"copy|{text}"
    )
    delete_btn = InlineKeyboardButton(
        "🗑 Delete", 
        callback_data="delete"
    )
    markup.add(copy_btn, delete_btn)
    return markup

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    text = message.text.strip()
    chat_id = str(message.chat.id)

    if not is_mlbb_format(text):
        return

    orders = load_orders()
    
    if chat_id not in orders:
        orders[chat_id] = []

    # ပြေစာတူ စစ်
    if text.lower() in [o.lower() for o in orders[chat_id]]:
        bot.reply_to(
            message,
            f"⚠️ *သတိပေးချက်!*\n\n`{text}`\n\nဒီ order တူတာ ပို့ထားပြီးပြီ!",
            parse_mode='Markdown'
        )
        return

    # သိမ်းထား
    orders[chat_id].append(text)
    save_orders(orders)

    # ပြန်ပို့
    bot.send_message(
        message.chat.id,
        f"✅ *MLBB Dia Order*\n\n`{text}`\n\n⬇️ အောက်က button နှိပ်ပါ",
        parse_mode='Markdown',
        reply_markup=make_keyboard(text)
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data

    if data.startswith("copy|"):
        text = data.split("|", 1)[1]
        # Copy message ပို့
        bot.send_message(
            call.message.chat.id,
            f"`{text}`",
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, "📋 Copy လုပ်ပြီး message ပို့ပြီ!")

    elif data == "delete":
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id, "🗑 ဖျက်ပြီး!")

bot.polling(none_stop=True)
