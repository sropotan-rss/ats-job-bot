import os
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from pdf_parser import extract_text
from vacancy_parser import parse_vacancy
from ai_engine import analyze
from report_generator import create_report

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

resume_storage = {}
result_storage = {}

menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("📄 Загрузить резюме", callback_data="resume")],
    [InlineKeyboardButton("💼 Анализ вакансии", callback_data="vacancy")],
    [InlineKeyboardButton("📊 PDF отчет", callback_data="report")],
    [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "AI бот анализа резюме\n\nВыберите действие:",
        reply_markup=menu
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    if query.data == "resume":

        await query.message.reply_text(
            "Отправьте PDF файл резюме."
        )

    elif query.data == "vacancy":

        await query.message.reply_text(
            "Отправьте ссылку или текст вакансии."
        )

    elif query.data == "report":

        user = query.from_user.id

        if user not in result_storage:

            await query.message.reply_text(
                "Сначала сделайте анализ."
            )
            return

        file = create_report(result_storage[user])

        await query.message.reply_document(
            document=open(file, "rb")
        )

    elif query.data == "help":

        await query.message.reply_text(
            "1️⃣ Загрузите PDF резюме\n"
            "2️⃣ Отправьте вакансию\n"
            "3️⃣ Получите ATS анализ\n"
            "4️⃣ Скачайте PDF отчет"
        )


async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):

    file = await update.message.document.get_file()

    path = f"{update.message.from_user.id}.pdf"

    await file.download_to_drive(path)

    text = extract_text(path)

    resume_storage[update.message.from_user.id] = text

    await update.message.reply_text(
        "Резюме получено ✅\n\nТеперь отправьте вакансию."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user not in resume_storage:

        await update.message.reply_text(
            "Сначала загрузите резюме."
        )
        return

    vacancy = update.message.text

    if vacancy.startswith("http"):
        vacancy = parse_vacancy(vacancy)

    resume = resume_storage[user]

    await update.message.reply_text("Анализирую...")

    result = analyze(resume, vacancy)

    result_storage[user] = result

    await update.message.reply_text(result)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
