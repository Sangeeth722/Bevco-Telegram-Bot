from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

conn = sqlite3.connect('prices.db', check_same_thread=False)

async def start(update: Update, context):
    await update.message.reply_text(
        "Send a brand name to search prices.\nExample: BACARDI MANGO CHILLI"
    )

async def search(update: Update, context):
    text = update.message.text.strip().lower()

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT Description, Volume, Price 
        FROM price_list 
        WHERE LOWER(Description) LIKE ? 
        LIMIT 20
        """,
        (f"%{text}%",)
    )

    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text(
            "No results found. Please check the spelling or this liquor may not be available at this BEVCO outlet."
        )
        return

    # Group manually
    grouped = {}

    for description, volume, price in rows:
        if description not in grouped:
            grouped[description] = []
        grouped[description].append((volume, price))

    msg = ""

    for name, items in grouped.items():
        msg += f"🍾 {name}\n"
        for volume, price in sorted(items):
            msg += f"   {volume} ml → ₹{price}\n"
        msg += "\n"

    await update.message.reply_text(msg)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

app.run_polling()
