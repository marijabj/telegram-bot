import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import db  # tvoj db.py modul

# ================= Environment Variables =================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
RAILWAY_URL = os.getenv("RAILWAY_URL")  # npr. https://telegram-bot.up.railway.app
PORT = int(os.environ.get("PORT", 8443))  # Railway prosleđuje port

# ================= Logging =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# ================= Command Handlers =================
async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"User ID: {user.id}\nUsername: @{user.username}")

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id != ADMIN_ID:
        await update.message.reply_text("Samo admin može dodavati korisnike!")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Upotreba: /add_user <user_id> <username>")
        return

    try:
        user_id = int(context.args[0])
        username = context.args[1]
    except ValueError:
        await update.message.reply_text("User ID mora biti broj.")
        return

    try:
        db.add_user(user_id, username)
        await update.message.reply_text(f"Korisnik @{username} dodat u bazu!")
    except Exception as e:
        logging.error(f"DB error: {e}")
        await update.message.reply_text("Došlo je do greške prilikom dodavanja korisnika.")

# ================= Main =================
def main():
    # Napravi tabelu ako ne postoji
    db.init_db()

    # Telegram app
    app = ApplicationBuilder().token(TOKEN).build()

    # Registracija komandi
    app.add_handler(CommandHandler("get_user_info", get_user_info))
    app.add_handler(CommandHandler("add_user", add_user))

    # Webhook setup
    webhook_url = f"{RAILWAY_URL}/{TOKEN}"
    print(f"Starting webhook on {webhook_url} at port {PORT}")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()

