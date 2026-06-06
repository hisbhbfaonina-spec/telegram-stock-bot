import os
import telebot
from database import conn, cursor

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN not found!")

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

ADMINS = [7562995992]  # নিজের Telegram ID বসাও

# =================== START ===================
@bot.message_handler(commands=['start'])
def start(message):
    cursor.execute(
        "INSERT OR IGNORE INTO users(telegram_id) VALUES(?)",
        (message.from_user.id,)
    )
    conn.commit()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛒 Shop", "💰 Balance")
    markup.row("💳 Deposit", "📦 My Orders")
    bot.send_message(
        message.chat.id,
        "Welcome To Edu API Key Shop",
        reply_markup=markup
    )

# =================== BALANCE ===================
@bot.message_handler(func=lambda m: m.text=="💰 Balance")
def balance(message):
    cursor.execute("SELECT balance FROM users WHERE telegram_id=?", (message.from_user.id,))
    row = cursor.fetchone()
    bot.send_message(message.chat.id, f"💰 Balance: {row[0]} TK" if row else "💰 Balance: 0 TK")

# =================== SHOP ===================
@bot.message_handler(func=lambda m: m.text=="🛒 Shop")
def shop(message):
    cursor.execute("SELECT id,name,price FROM products")
    rows = cursor.fetchall()
    if not rows:
        bot.send_message(message.chat.id, "No Products Available")
        return
    text = "📦 Products\n\n" + "\n".join(f"{p[0]}. {p[1]} - {p[2]} TK" for p in rows) + "\n\nSend Product ID"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, process_buy)

def process_buy(message):
    try:
        product_id = int(message.text)
        cursor.execute("SELECT name,price FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()
        if not product:
            bot.send_message(message.chat.id, "Invalid Product")
            return
        bot.send_message(message.chat.id, f"{product[0]}\nPrice: {product[1]} TK\nSend Quantity")
        bot.register_next_step_handler(message, process_quantity, product_id, product[1])
    except:
        bot.send_message(message.chat.id, "Invalid Input")

def process_quantity(message, product_id, price):
    try:
        qty = int(message.text)
        total = qty * price
        cursor.execute("SELECT balance FROM users WHERE telegram_id=?", (message.from_user.id,))
        balance = cursor.fetchone()[0]
        if balance < total:
            bot.send_message(message.chat.id, f"❌ Need {total} TK")
            return
        cursor.execute("SELECT id,item FROM stock WHERE product_id=? AND sold=0 LIMIT ?", (product_id, qty))
        items = cursor.fetchall()
        if len(items) < qty:
            bot.send_message(message.chat.id, "❌ Out Of Stock")
            return
        delivered = []
        for item in items:
            cursor.execute("UPDATE stock SET sold=1 WHERE id=?", (item[0],))
            delivered.append(item[1])
        cursor.execute("UPDATE users SET balance=balance-? WHERE telegram_id=?", (total, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, "✅ Purchase Success\n\n" + "\n".join(delivered))
    except:
        bot.send_message(message.chat.id, "Invalid Quantity")

# =================== DEPOSIT ===================
@bot.message_handler(func=lambda m: m.text=="💳 Deposit")
def deposit(message):
    bot.send_message(message.chat.id, "Send Amount")
    bot.register_next_step_handler(message, deposit_amount)

def deposit_amount(message):
    try:
        amount = int(message.text)
        bot.send_message(message.chat.id, f"Send TRXID for amount {amount} TK")
        bot.register_next_step_handler(message, save_trx, amount)
    except:
        bot.send_message(message.chat.id, "Invalid Amount")

def save_trx(message, amount):
    try:
        trxid = message.text
        user_id = message.from_user.id
        cursor.execute("INSERT INTO deposits(user_id,amount,trxid,status) VALUES(?,?,?,?)", (user_id, amount, trxid, "approved"))
        cursor.execute("UPDATE users SET balance=balance+? WHERE telegram_id=?", (amount, user_id))
        conn.commit()
        bot.send_message(message.chat.id, f"✅ Deposit Successful\n💰 {amount} TK Added To Your Balance")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

# =================== ADMIN ===================
@bot.message_handler(commands=['add_product'])
def add_product(message):
    if message.from_user.id not in ADMINS: return
    bot.send_message(message.chat.id, "Send Name:Price")
    bot.register_next_step_handler(message, save_product)

def save_product(message):
    try:
        name, price = message.text.split(":")
        cursor.execute("INSERT INTO products(name,price) VALUES(?,?)", (name, int(price)))
        conn.commit()
        bot.send_message(message.chat.id, "✅ Product Added")
    except:
        bot.send_message(message.chat.id, "Wrong Format")

@bot.message_handler(commands=['add_stock'])
def add_stock(message):
    if message.from_user.id not in ADMINS: return
    bot.send_message(message.chat.id, "Send ProductID:VoucherCode")
    bot.register_next_step_handler(message, save_stock)

def save_stock(message):
    try:
        product_id, item = message.text.split(":",1)
        cursor.execute("INSERT INTO stock(product_id,item) VALUES(?,?)", (int(product_id), item))
        conn.commit()
        bot.send_message(message.chat.id, "✅ Stock Added")
    except:
        bot.send_message(message.chat.id, "Wrong Format")

@bot.message_handler(commands=['stock'])
def stock(message):
    if message.from_user.id not in ADMINS: return
    cursor.execute("SELECT products.name,COUNT(stock.id) FROM stock JOIN products ON stock.product_id=products.id WHERE sold=0 GROUP BY products.name")
    rows = cursor.fetchall()
    text = "Stock Status\n\n" + "\n".join(f"{r[0]} : {r[1]}" for r in rows) if rows else "No Stock"
    bot.send_message(message.chat.id, text)

# =================== RUN BOT ===================
print("Bot Started")
bot.infinity_polling(skip_pending=True, long_polling_timeout=60)
