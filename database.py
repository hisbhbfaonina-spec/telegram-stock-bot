def save_trx(message, amount):
    try:
        trxid = message.text
        user_id = message.from_user.id

        cursor.execute("""
        INSERT INTO deposits
        (user_id, amount, trxid, status)
        VALUES (?, ?, ?, ?)
        """, (
            user_id,
            amount,
            trxid,
            "approved"
        ))

        cursor.execute("""
        UPDATE users
        SET balance = balance + ?
        WHERE telegram_id = ?
        """, (
            amount,
            user_id
        ))

        conn.commit()

        bot.send_message(
            message.chat.id,
            f"✅ Deposit Successful\n💰 {amount} TK Added To Your Balance"
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"Error: {e}"
        )
