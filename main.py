import telebot
import os

# Bot Token from Railway Environment Variable
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN not found!")

bot = telebot.TeleBot(TOKEN)

# Remove webhook if exists (fix 409 error)
bot.remove_webhook()

# Admin IDs
admins = [7562995992]  # Replace with your Telegram ID

# Initial stock
stock = [
    "gmail1@gmail.com:pass123",
    "gmail2@gmail.com:pass456",
    "gmail3@gmail.com:pass789"
]

# ---------------- COMMANDS ----------------

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🛒 Telegram Stock Bot Online ✅\n\n/buy - Buy Stock"
    )

# /buy command
@bot.message_handler(commands=['buy'])
def buy(message):
    if len(stock) == 0:
        bot.send_message(message.chat.id, "❌ Out Of Stock")
        return
    bot.send_message(
        message.chat.id,
        "📦 Stock Available\n💵 Price: 200 TK\nReply YES to confirm purchase."
    )
    bot.register_next_step_handler(message, confirm_buy)

# Buy confirmation
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

# /check_stock (admin only)
@bot.message_handler(commands=['check_stock'])
def check_stock(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "❌ You are not admin")
        return
    bot.send_message(
        message.chat.id,
        f"📦 Stock Left: {len(stock)}"
    )

# /add_stock (admin only)
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
    new_stock = [line.strip() for line in message.text.split("\n") if line.strip()]
    stock.extend(new_stock)
    bot.send_message(
        message.chat.id,
        f"✅ Added {len(new_stock)} stock(s)"
    )

# ---------------- RUN BOT ----------------
print("Bot Started...")
bot.infinity_polling(skip_pending=True, long_polling_timeout=60)
