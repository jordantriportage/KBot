import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# CONFIGURATION
TOKEN = "8075326221:AAGUWWMNUdvww4-TILy54R8zyZzz--Pvgxc"
ADMIN_IDS = [8493969803]
GROUPE_ID = -5156847371

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

updater = Updater(TOKEN)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, annonce))
dp.add_handler(CallbackQueryHandler(bouton, pattern="ok"))
print("✅ Bot lancé")
updater.start_polling()
updater.idle()
