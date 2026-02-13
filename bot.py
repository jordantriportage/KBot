import re
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# === CONFIGURATION ===
# !!! IMPORTANT: Double-check these values are correct !!!
TOKEN = "8075326221:AAGUWWMNUdvww4-TILy54R8zyZzz--Pvgxc"
ADMIN_IDS = [8493969803]  # Your ID
GROUPE_ID = -5156847371  # Your Group ID

# --- 1. THE DUMMY FLASK WEB SERVER (for health checks) ---
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    # This simple response keeps Koyeb happy
    return "Bot is running", 200

def run_flask():
    # Runs the Flask app on the required port (8000)
    flask_app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)

# Start Flask in a background thread so it runs in parallel with your bot
# This is the magic that makes it work [citation:2][citation:4][citation:5]
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
# -----------------------------------------------------------

# --- 2. YOUR TELEGRAM BOT CODE (slightly simplified for reliability) ---
def start(update, context):
    update.message.reply_text(
        "✅ Bot prêt !\n\n"
        "Envoie :\n"
        "TITRE : ...\n"
        "ORGANISME : ...\n"
        "DATE LIMITE : ...\n"
        "LIEN : ..."
    )

def annonce(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        return
    texte = update.message.text
    titre = re.search(r"TITRE\s*:\s*(.+)", texte, re.IGNORECASE)
    msg = f"📢 {titre.group(1) if titre else 'Nouvelle offre'}"
    bouton = [[InlineKeyboardButton("✅ Intéressé", callback_data="ok")]]
    context.bot.send_message(
        GROUPE_ID,
        msg,
        reply_markup=InlineKeyboardMarkup(bouton)
    )
    update.message.reply_text("✅ Publié !")

def bouton(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    for admin in ADMIN_IDS:
        context.bot.send_message(admin, f"🔔 {user.full_name} intéressé")

print("✅ Bot et serveur Flask démarrés")
updater = Updater(TOKEN)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, annonce))
dp.add_handler(CallbackQueryHandler(bouton, pattern="ok"))
updater.start_polling()
updater.idle()
# ----------------------------------------------------------------------
