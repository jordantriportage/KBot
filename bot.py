import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = "7244281986:AAHyQE7rMPElsW77a1LuSrti9ROVXlbCY_M"
GROUP_CHAT_ID = -100XXXXXXXXXX

MANAGERS = {
    "Manager 1": 123456789,
    "Manager 2": 987654321,
}

logging.basicConfig(level=logging.INFO)

opportunities = {}
interest_counts = {}
user_choices = {}          # user_id -> opportunity_id
user_manager_choice = {}   # user_id -> manager_name
interested_users = {}      # opportunity_id -> set(user_ids)


# 🟢 /new en privé
async def new_opportunity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    await update.message.reply_text(
        "Envoie l'opportunité avec ce format :\n\n"
        "TITRE : ...\n"
        "ORGANISME : ...\n"
        "DATE LIMITE : ...\n"
        "LIEU : ...\n"
        "DESCRIPTION : ...\n"
        "LIEN : ..."
    )


# 🟢 Réception template
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    text = update.message.text

    required_fields = [
        "TITRE :", "ORGANISME :", "DATE LIMITE :",
        "LIEU :", "DESCRIPTION :", "LIEN :"
    ]

    if not all(field in text for field in required_fields):
        await update.message.reply_text("❌ Format incorrect.")
        return

    opportunity_id = len(opportunities) + 1

    opportunities[opportunity_id] = {
        "text": text,
        "message_id": None
    }

    interest_counts[opportunity_id] = 0
    interested_users[opportunity_id] = set()

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Je suis intéressé", callback_data=f"interesse|{opportunity_id}"),
            InlineKeyboardButton("📋 Voir les intéressés", callback_data=f"liste|{opportunity_id}")
        ]
    ])

    message = f"{text}\n\n👥 Intéressés : 0"

    sent_message = await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=message,
        reply_markup=keyboard
    )

    opportunities[opportunity_id]["message_id"] = sent_message.message_id

    await update.message.reply_text("✅ Opportunité envoyée dans le groupe.")


# 🟢 Gestion boutons
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    # 👉 Clique sur "Je suis intéressé"
    if data.startswith("interesse|"):
        opportunity_id = int(data.split("|")[1])

        if user_id in interested_users[opportunity_id]:
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Tu es déjà enregistré comme intéressé."
            )
            return

        interested_users[opportunity_id].add(user_id)
        user_choices[user_id] = opportunity_id

        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"manager|{name}")]
            for name in MANAGERS.keys()
        ]

        await context.bot.send_message(
            chat_id=user_id,
            text="Avec quel manager es-tu en contact ?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        interest_counts[opportunity_id] += 1
        count = interest_counts[opportunity_id]

        opportunity = opportunities[opportunity_id]
        new_text = f"{opportunity['text']}\n\n👥 Intéressés : {count}"

        keyboard_group = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Je suis intéressé", callback_data=f"interesse|{opportunity_id}"),
                InlineKeyboardButton("📋 Voir les intéressés", callback_data=f"liste|{opportunity_id}")
            ]
        ])

        await context.bot.edit_message_text(
            chat_id=GROUP_CHAT_ID,
            message_id=opportunity["message_id"],
            text=new_text,
            reply_markup=keyboard_group
        )

    # 👉 Choix manager
    elif data.startswith("manager|"):
        manager_name = data.split("|")[1]
        manager_id = MANAGERS.get(manager_name)
        user = query.from_user

        opportunity_id = user_choices.get(user.id)
        opportunity = opportunities.get(opportunity_id)

        user_manager_choice[user.id] = manager_name

        if manager_id and opportunity:
            await context.bot.send_message(
                chat_id=manager_id,
                text=(
                    f"📢 Nouveau consultant intéressé\n\n"
                    f"👤 {user.full_name} (@{user.username})\n"
                    f"🧑‍💼 Manager : {manager_name}\n\n"
                    f"{opportunity['text']}"
                )
            )

        await context.bot.send_message(
            chat_id=user.id,
            text=f"✅ Manager sélectionné : {manager_name}\nIl a été notifié."
        )

    # 👉 Liste des intéressés (managers only)
    elif data.startswith("liste|"):
        opportunity_id = int(data.split("|")[1])

        if user_id not in MANAGERS.values():
            await query.answer("❌ Réservé aux managers", show_alert=True)
            return

        users = interested_users.get(opportunity_id, set())

        if not users:
            await context.bot.send_message(
                chat_id=user_id,
                text="Aucun consultant intéressé pour le moment."
            )
            return

        message = "📋 Consultants intéressés :\n\n"

        for uid in users:
            try:
                chat = await context.bot.get_chat(uid)
                name = chat.full_name
                username = f"@{chat.username}" if chat.username else ""
                manager = user_manager_choice.get(uid, "Non sélectionné")
                message += f"• {name} {username} → {manager}\n"
            except:
                manager = user_manager_choice.get(uid, "Non sélectionné")
                message += f"• ID : {uid} → {manager}\n"

        await context.bot.send_message(
            chat_id=user_id,
            text=message
        )


# 🟢 Lancement
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("new", new_opportunity))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_private_message))

    print("🤖 Bot lancé")
    app.run_polling()


if __name__ == "__main__":
    main()
