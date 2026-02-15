import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import init_db, add_user, user_exists

TOKEN = os.getenv("8278457315:AAEKRKEPT68yZDIC2OtosjQy-Q5aR_whGjU")
ADMIN_ID = int(os.getenv("8575573468"))
PORT = int(os.environ.get("PORT", 8443))  # Railway port
RAILWAY_URL = "https://your-railway-app.up.railway.app"  # zameni sa tvojim URL

# ---- komande ----
async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user_exists(user.id):
        await update.message.reply_text("⛔ Nemate pristup")
        return
    await update.message.reply_text(f"ID: {user.id}\nUsername: @{user.username}")

async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Samo admin može dodavati korisnike")
        return
    if len(context.args) != 2:
        await update.message.reply_text("Korišćenje: /add_user <user_id> <username>")
        return
    try:
        user_id = int(context.args[0])
        username = context.args[1]
        add_user(user_id, username)
        await update.message.reply_text(f"✅ Korisnik {username} je dodat")
    except Exception as e:
        await update.message.reply_text(f"❌ Greška: {e}")

# ---- main ----
def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("get_user_info", get_user_info))
    app.add_handler(CommandHandler("add_user", add_user_command))

    webhook_url = f"{RAILWAY_URL}/{TOKEN}"
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()

