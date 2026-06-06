import telebot
import os

# Railway Variable
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN not found!")

bot = telebot.TeleBot(TOKEN)

# Admin ID
admins = [7562995992]

# Demo Stock
stock = [
    "gmail1@gmail.com:pass123",
    "gmail2@gmail.com:pass456",
    "gmail3@gmail.com:pass789"
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🛒 Telegram Stock Bot Online ✅\n\n/buy - Buy Stock"
    )

@bot.message_handler(commands=['buy'])
def buy(message):
    if len(stock) == 0:
        bot.send_message(message.chat.id, "❌ Out Of Stock")
        return

    bot.send_message(
        message.chat.id,
        "📦 Stock Available\n\nReply YES to confirm purchase."
    )
    bot.register_next_step_handler(message, confirm_buy)

def confirm_buy(message):
    global stock

    if message.text.upper() != "YES":
        bot.send_message(message.chat.id, "❌ Purchase Cancelled")
        return

    if len(stock) == 0:
        bot.send_message(message.chat.id, "❌ Out Of Stock")
        return

    item = stock.pop(0)

    bot.send_message(
        message.chat.id,
        f"✅ Purchase Success\n\n{item}"
    )

@bot.message_handler(commands=['check_stock'])
def check_stock(message):

    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "❌ You are not admin")
        return

    bot.send_message(
        message.chat.id,
        f"📦 Stock Left: {len(stock)}"
    )

@bot.message_handler(commands=['add_stock'])
def add_stock(message):

    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "❌ You are not admin")
        return

    bot.send_message(
        message.chat.id,
        "Send stock list.\nOne stock per line."
    )

    bot.register_next_step_handler(message, save_stock)

def save_stock(message):
    global stock

    new_stock = []

    for line in message.text.split("\n"):
        line = line.strip()

        if line:
            stock.append(line)
            new_stock.append(line)

    bot.send_message(
        message.chat.id,
        f"✅ Added {len(new_stock)} stock(s)"
    )

print("Bot Started...")
bot.infinity_polling(skip_pending=True)
