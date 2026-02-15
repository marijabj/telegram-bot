import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import init_db, add_user, user_exists

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
RAILWAY_URL = os.getenv("RAILWAY_URL")

# Init DB
init_db()

# Telegram app
telegram_app = ApplicationBuilder().token(TOKEN).build()

# ================= KOMANDE =================

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"User ID: {user.id}\nUsername: {user.username}"
    )

async def add_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Nemaš permisiju.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Upotreba: /add_user user_id username")
        return

    user_id = int(context.args[0])
    username = context.args[1]
    add_user(user_id, username)
    await update.message.reply_text(f"✅ Korisnik {username} dodat.")

telegram_app.add_handler(CommandHandler("get_user_info", get_user_info))
telegram_app.add_handler(CommandHandler("add_user", add_user_cmd))

# ================= FASTAPI SERVER =================

app = FastAPI()

@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(f"{RAILWAY_URL}/webhook")
    print("Webhook postavljen!")

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

