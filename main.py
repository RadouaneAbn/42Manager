#!/bin/env python3

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from time import time
import os
import asyncio
from src.utils.logger import log_info, log_error, log_warning
from datetime import datetime, timedelta

from dotenv import load_dotenv

log_info("Info Message")
log_warning("Warning Message")
log_error("Error Message")

load_dotenv()

LOCK_FILE = "/home/rabounou/.lock_time"
USER_ID = os.environ.get("USER_ID")
BOT_USERNAME = os.environ.get("BOT_USERNAME")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

delete_queue = []

async def schedule_deletion(chat_id, message_id, delay_seconds=3600):
    deletion_time = datetime.now() + timedelta(seconds=delay_seconds)
    delete_queue.append((deletion_time, chat_id, message_id))

async def deletion_worker(bot):
    while True:
        now = datetime.now()
        for item in delete_queue[:]:  # copy to avoid mutation issues
            deletion_time, chat_id, message_id = item
            if now >= deletion_time:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception as e:
                    print(f"Delete failed: {e}")
                delete_queue.remove(item)
        await asyncio.sleep(60)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user_id = update.effective_user.id
    # await update.message.reply_text(user_id)
    msg = await update.message.reply_text("Hello, what can i do for you!")
    await schedule_deletion(msg.chat.id, msg.message_id)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("tell me what you want\n/check\n/logtime")
    await schedule_deletion(msg.chat.id, msg.message_id)

async def logtime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Soon !!!")
    await schedule_deletion(msg.chat.id, msg.message_id)


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("what do you want to customize")
    await schedule_deletion(msg.chat.id, msg.message_id)

async def start_lock_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        line = ""
        with open (LOCK_FILE, "r") as f:
            line: str = f.readline().strip()
        if not line.isnumeric():
            msg = await update.message.reply_text("The screen is not locked `correctly`.")
            await schedule_deletion(msg.chat.id, msg.message_id)
            return
        lock_time = int(line)
        current_time = int(time())
        timeout = lock_time + (60*37)

        if current_time < timeout:
            remaining = timeout - current_time
            minutes = remaining //60
            msg = await update.message.reply_text(f"Screen is still locked. {minutes}m left before logout.🔓")
            await schedule_deletion(msg.chat.id, msg.message_id)
        else:
            msg = await update.message.reply_text("Screen is not locked or timeout has passed.🔓")
            await schedule_deletion(msg.chat.id, msg.message_id)
    except FileNotFoundError:
        msg = await update.message.reply_text("Screen is not locked or timeout has passed.🔓")
        await schedule_deletion(msg.chat.id, msg.message_id)
    except Exception as e:
        log_error("start lock check command error")


async def background_lock_monitor(bot):
    while True:
        try:
            if not os.path.exists(LOCK_FILE):
                # await bot.send_message(chat_id=USER_ID, text="Screen is not locked or .lock_time missing 🔓.")
                await asyncio.sleep(60)
                continue

            with open(LOCK_FILE, "r") as f:
                line: str = f.readline().strip()

            if not line.isnumeric():
                # await bot.send_message(chat_id=USER_ID, text="The screen is not locked correctly ⚠️.")
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
                        msg = await bot.send_message(chat_id=USER_ID, text="You are about to be logged out ⚠️⚠️⚠️")
                        await schedule_deletion(msg.chat.id, msg.message_id)
                    else:
                        msg = await bot.send_message(chat_id=USER_ID, text=f"{minutes}m left before logout.")
                        await schedule_deletion(msg.chat.id, msg.message_id)
                    await asyncio.sleep(60)
                else:
                    await asyncio.sleep(60)
            else:
                await asyncio.sleep(600)
                return

        except Exception as e:
            # await bot.send_message(chat_id=USER_ID, text=f"⚠️ Error in lock monitor: {str(e)}")
            await asyncio.sleep(60)  # Check every minute

# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

async def post_init(application: Application):
    application.create_task(background_lock_monitor(application.bot))
    application.create_task(deletion_worker(application.bot))


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler(["help", "h"], help_command))
    app.add_handler(CommandHandler(["logtime", "lg"], logtime_command))
    # app.add_handler(CommandHandler("h", help_command))
    app.add_handler(CommandHandler("check", start_lock_check_command))
    print("Starting bot...")
    app.run_polling(poll_interval=3)

if __name__ == "__main__":
    main()