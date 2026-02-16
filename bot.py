import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
RAILWAY_URL = os.getenv("RAILWAY_URL")  # npr. https://your-project.up.railway.app

# Telegram bot aplikacija (webhook-only)
telegram_app = ApplicationBuilder().token(TOKEN).build()

# ================= KOMANDE =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("BOT RADI ✅")

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            f"Hello {update.effective_user.first_name} ({update.effective_user.id})"
        )

async def add_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ Nemaš permisiju.")
            return

        if len(context.args) != 2:
            await update.message.reply_text("Upotreba: /add_user user_id username")
            return

        user_id = int(context.args[0])
        username = context.args[1]
        # ovde pozivaš svoju funkciju iz db.py
        # add_user(user_id, username)
        await update.message.reply_text(f"✅ Korisnik {username} dodat.")

# Dodaj komande botu
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("get_user_info", get_user_info))
telegram_app.add_handler(CommandHandler("add_user", add_user_cmd))

# ================= FASTAPI SERVER =================

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True}

@app.on_event("startup")
async def startup():
    # samo initialize, ne start
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(f"{RAILWAY_URL}/webhook")
    print("Webhook postavljen na:", f"{RAILWAY_URL}/webhook")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("UPDATE:", data)
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"ok": True}
    except Exception as e:
        print("ERROR:", e)
        return {"ok": False, "error": str(e)}

