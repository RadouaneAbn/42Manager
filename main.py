#!/bin/env python3

from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from time import sleep, time
import os
import asyncio


LOCK_FILE = "/home/rabounou/.lock_time"
TOKEN: Final = "7888005955:AAEbrynGhQ_U-Rj564ompvS3uOJhDpZckpQ"
BOT_USERNAME: Final = "loggingmasterbot"
USER_ID = "7862638491"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(user_id)
    await update.message.reply_text("Hello, what can i do for you! ")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("tell me what you want")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("what do you want to customize")

async def start_lock_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        line = ""
        with open (LOCK_FILE, "r") as f:
            line: str = f.readline().strip()
        if not line.isnumeric():
            await update.message.reply_text("The screen is not locked `correctly`.")
            return
        lock_time = int(line)
        current_time = int(time())
        timeout = lock_time + (60*37)

        if current_time < timeout:
            remaining = timeout - current_time
            minutes = remaining //60
            await update.message.reply_text(f"Screen is still locked. {minutes}m left before logout.🔓")
        else:
            await update.message.reply_text("Screen is not locked or timeout has passed.🔓")
    except FileNotFoundError:
        await update.message.reply_text("Screen is not locked or timeout has passed.🔓")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}⚠️")


async def background_lock_monitor(bot):
    while True:
        try:
            if not os.path.exists(LOCK_FILE):
                await bot.send_message(chat_id=USER_ID, text="Screen is not locked or .lock_time missing 🔓.")
                await asyncio.sleep(60)
                continue

            with open(LOCK_FILE, "r") as f:
                line: str = f.readline().strip()

            if not line.isnumeric():
                await bot.send_message(chat_id=USER_ID, text="The screen is not locked correctly ⚠️.")
                await asyncio.sleep(60)
                continue

            lock_time = int(line)
            current_time = int(time())
            timeout = lock_time + (60 * 37)
            remaining = timeout - current_time

            if remaining > 0:
                minutes = remaining // 60

                if minutes <= 7:
                    if (minutes == 1):
                        await bot.send_message(chat_id=USER_ID, text="You are about to be logged out ⚠️⚠️⚠️")
                    else:
                        await bot.send_message(chat_id=USER_ID, text=f"{minutes}m left before logout.")
                    await asyncio.sleep(60)
                else:
                    await asyncio.sleep(60)
            else:
                await asyncio.sleep(600)
                return

        except Exception as e:
            await bot.send_message(chat_id=USER_ID, text=f"⚠️ Error in lock monitor: {str(e)}")
            await asyncio.sleep(60)  # Check every minute

# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

async def post_init(application: Application):
    application.create_task(background_lock_monitor(application.bot))


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("check", start_lock_check_command))

    print("Starting bot...")
    app.run_polling(poll_interval=3)