import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import init_db, add_user, user_exists

# Pokretanje baze (kreira tabelu users ako ne postoji)
init_db()

# Token i Admin ID iz env varijabli
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))  # ID admina

print("BOT_TOKEN:", os.getenv("BOT_TOKEN"))
print("ADMIN_ID:", os.getenv("ADMIN_ID"))

if not TOKEN:
    raise ValueError("BOT_TOKEN nije definisan!")

# ---------- HANDLERI ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pozdravna poruka kada korisnik startuje bota."""
    await update.message.reply_text(
        f"Pozdrav, {update.effective_user.first_name}! Dobrodošao/la na bot."
    )

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Vrati user_id i username korisnika koji je poslao komandu."""
    user = update.effective_user
    await update.message.reply_text(
        f"User ID: {user.id}\nUsername: @{user.username if user.username else 'N/A'}"
    )

async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dodavanje korisnika u bazu, samo za admina."""
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("Nemate ovlašćenje za ovu komandu.")
        return

    # Očekujemo dva argumenta: user_id username
    if len(context.args) != 2:
        await update.message.reply_text("Korišćenje: /add_user user_id username")
        return

    try:
        new_user_id = int(context.args[0])
        username = context.args[1]
        add_user(new_user_id, username)
        await update.message.reply_text(f"Korisnik @{username} dodat u bazu.")
    except ValueError:
        await update.message.reply_text("user_id mora biti broj.")

# ---------- MAIN ----------

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Dodavanje handlera
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get_user_info", get_user_info))
    app.add_handler(CommandHandler("add_user", add_user_command))

    # Pokreni bota asinhrono
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

