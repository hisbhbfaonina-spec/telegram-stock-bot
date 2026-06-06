import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN not found!")

bot = telebot.TeleBot(TOKEN)

# Remove webhook (fix 409 error)
bot.remove_webhook()

admins = [7562995992]

products = {
    1: {
        "name": "Netflix",
        "price": 300,
        "stock": []
    },
    2: {
        "name": "Spotify",
        "price": 150,
        "stock": []
    },
    3: {
        "name": "Canva Pro",
        "price": 250,
        "stock": []
    }
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🛒 Shop Bot Online ✅\n\n/products - View Products"
    )

@bot.message_handler(commands=['products'])
def products_list(message):
    text = "📦 Available Products\n\n"

    for pid, product in products.items():
        text += f"{pid}. {product['name']} - {product['price']} TK\n"

    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['buy'])
def buy(message):
    bot.send_message(
        message.chat.id,
        "Send Product ID"
    )

    bot.register_next_step_handler(message, process_buy)

def process_buy(message):
    try:
        product_id = int(message.text)

        if product_id not in products:
            bot.send_message(message.chat.id, "❌ Invalid Product ID")
            return

        product = products[product_id]

        bot.send_message(
            message.chat.id,
            f"📦 {product['name']}\n💰 Price: {product['price']} TK\n\nReply YES"
        )

        bot.register_next_step_handler(
            message,
            confirm_buy,
            product_id
        )

    except:
        bot.send_message(message.chat.id, "❌ Invalid Input")

def confirm_buy(message, product_id):
    if message.text.upper() != "YES":
        bot.send_message(message.chat.id, "❌ Purchase Cancelled")
        return

    if len(products[product_id]["stock"]) == 0:
        bot.send_message(message.chat.id, "❌ Out Of Stock")
        return

    item = products[product_id]["stock"].pop(0)

    bot.send_message(
        message.chat.id,
        f"✅ Purchase Success\n\n{item}"
    )

@bot.message_handler(commands=['add_stock'])
def add_stock(message):

    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "❌ You are not admin")
        return

    bot.send_message(
        message.chat.id,
        "Send:\nProductID:Stock"
    )

    bot.register_next_step_handler(
        message,
        save_stock
    )

def save_stock(message):
    try:
        product_id, item = message.text.split(":", 1)

        product_id = int(product_id)

        if product_id not in products:
            bot.send_message(message.chat.id, "❌ Invalid Product ID")
            return

        products[product_id]["stock"].append(item)

        bot.send_message(
            message.chat.id,
            "✅ Stock Added"
        )

    except:
        bot.send_message(
            message.chat.id,
            "❌ Format: ProductID:Stock"
        )

@bot.message_handler(commands=['check_stock'])
def check_stock(message):

    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "❌ You are not admin")
        return

    text = "📦 Stock Status\n\n"

    for pid, product in products.items():
        text += f"{product['name']} = {len(product['stock'])}\n"

    bot.send_message(message.chat.id, text)

print("Bot Started...")

bot.infinity_polling(
    skip_pending=True,
    long_polling_timeout=60
)
