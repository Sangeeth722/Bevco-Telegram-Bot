from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

conn =sqlite3.connect('prices.db',check_same_thread=False)

async def start(update:Update ,context):
    await update.message.reply_text("Send a brand name to search prices.\nExample: BACARDI MANGO CHILLI")

async def search(update:Update ,context):
    text = update.message.text

    query ="""
    SELECT * FROM price_list WHERE Description LIKE LOWER(?) LIMIT 20 
    """
    df = pd.read_sql(query,conn, params=('%' +text + '%',))

    if df.empty:
        await update.message.reply_text('No results found. Please check the spelling or this liquor may not be available at this BEVCO outlet.')
        return
    msg = ""

    grouped = df.groupby("Description")

    for name, group in grouped:
        msg += f"🍾 {name}\n"
        for _, row in group.iterrows():
            msg += f"   {row['Volume']} ml → ₹{row['Price']}\n"
            msg += "\n"


    await update.message.reply_text(msg)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler('start',start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
app.run_polling()