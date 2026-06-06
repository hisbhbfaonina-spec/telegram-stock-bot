import telebot
import os

# Bot Token from Environment Variable
TOKEN = os.getenv("8560800126:AAHsudE0rH-IjV7eMJ3rfRoOqZeOm44tCO8")
bot = telebot.TeleBot(TOKEN)

# Stock list (initial stock)
stock = [
    "test1@gmail.com:123456",
    "test2@gmail.com:abcdef",
    "test3@gmail.com:pass789"
]

# Admins (Telegram IDs as integers)
admins = [
    7562995992  # Replace with your Telegram ID
]

# ===================== COMMANDS =====================

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🛒 Bot Online ✅\nUse /buy to get stock")

# /buy command
@bot.message_handler(commands=['buy'])
def buy(message):
    global stock
    if len(stock) == 0:
        bot.send_message(message.chat.id, "❌ Out Of Stock")
    else:
        bot.send_message(
            message.chat.id,
            "📦 Stock available!\n💵 Price: 200 TK\nType YES to confirm"
        )
        bot.register_next_step_handler(message, buy_confirm)

# Buy confirmation step
def buy_confirm(message):
    global stock
    if message.text.upper() == "YES":
        if len(stock) == 0:
            bot.send_message(message.chat.id, "❌ Out Of Stock")
        else:
            account = stock.pop(0)
            bot.send_message(message.chat.id, f"✅ Purchase Success\n\n{account}")
    else:
        bot.send_message(message.chat.id, "❌ Purchase Cancelled")

# /check_stock - Admin only
@bot.message_handler(commands=['check_stock'])
def check_stock(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "❌ You are not admin")
        return
    if len(stock) == 0:
        bot.send_message(message.chat.id, "No stock available")
    else:
        bot.send_message(message.chat.id, f"Current stock:\n{stock}")

# /add_stock - Admin only
@bot.message_handler(commands=['add_stock'])
def add_stock(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "❌ You are not admin")
        return
    bot.send_message(message.chat.id, "Send new stock, one per line")
    bot.register_next_step_handler(message, save_stock)

def save_stock(message):
    global stock
    lines = message.text.split("\n")
    for line in lines:
        line = line.strip()
        if line:
            stock.append(line)
    bot.send_message(message.chat.id, f"✅ Added {len(lines)} stock(s)")

# ===================== RUN BOT =====================
bot.infinity_polling()
