import os
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from pdf_parser import extract_text
from ai_engine import analyze

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

resume_storage = {}

menu_keyboard = ReplyKeyboardMarkup(
    [
        ["📄 Отправить резюме"],
        ["💼 Анализ вакансии"],
        ["ℹ️ Помощь"]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Привет 👋\n\nЯ бот для анализа резюме.\n\nВыбери действие:",
        reply_markup=menu_keyboard
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Инструкция:\n\n"
        "1️⃣ Нажми 'Отправить резюме'\n"
        "2️⃣ Загрузи PDF файл\n"
        "3️⃣ Отправь текст вакансии\n\n"
        "Бот рассчитает ATS совместимость."
    )


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "📄 Отправить резюме":

        await update.message.reply_text(
            "Отправь PDF файл резюме."
        )

    elif text == "💼 Анализ вакансии":

        await update.message.reply_text(
            "Сначала отправь резюме."
        )

    elif text == "ℹ️ Помощь":

        await help_command(update, context)


async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):

    file = await update.message.document.get_file()

    path = f"{update.message.from_user.id}.pdf"

    await file.download_to_drive(path)

    text = extract_text(path)

    resume_storage[update.message.from_user.id] = text

    await update.message.reply_text(
        "Резюме получено ✅\n\nТеперь отправь текст вакансии."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if user_id not in resume_storage:

        await update.message.reply_text(
            "Сначала отправь резюме."
        )
        return

    vacancy = update.message.text
    resume = resume_storage[user_id]

    await update.message.reply_text("Анализирую...")

    result = analyze(resume, vacancy)

    await update.message.reply_text(result)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)
    )

    app.add_handler(
        MessageHandler(filters.Document.PDF, handle_pdf)
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
