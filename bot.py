import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from parser import parse_hh
from ats_engine import analyze
from resume_reader import read_pdf
from hh_search import search_jobs


logging.basicConfig(level=logging.INFO)

resume_text = ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 AI Бот анализа резюме

Что я умею:

1️⃣ Отправь PDF резюме  
2️⃣ Отправь ссылку на вакансию hh.ru  

Я покажу:

📊 ATS оценку  
✅ подходящие навыки  
❌ чего не хватает  
💡 советы как улучшить резюме  

Команда поиска вакансий:

/jobs Product Manager
"""

    await update.message.reply_text(text)


async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global resume_text

    try:

        file = await update.message.document.get_file()

        await file.download_to_drive("resume.pdf")

        resume_text = read_pdf("resume.pdf")

        await update.message.reply_text("✅ Резюме загружено")

    except:

        await update.message.reply_text("❌ Ошибка чтения PDF")


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global resume_text

    try:

        url = update.message.text

        if "hh.ru" not in url:

            await update.message.reply_text("Отправь ссылку на вакансию hh.ru")

            return

        if not resume_text:

            await update.message.reply_text("Сначала отправь резюме PDF")

            return

        await update.message.reply_text("🔎 Анализирую вакансию...")

        vacancy = parse_hh(url)

        result = analyze(resume_text, vacancy)

        if len(result) > 4000:
            result = result[:4000]

        await update.message.reply_text(result)

    except Exception as e:

        logging.error(e)

        await update.message.reply_text("❌ Ошибка анализа")


async def jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        query = " ".join(context.args)

        if not query:

            await update.message.reply_text(
                "Пример:\n/jobs Product Manager"
            )
            return

        await update.message.reply_text("🔎 Ищу вакансии...")

        links = search_jobs(query)

        text = "🔥 Найденные вакансии:\n\n"

        for l in links[:10]:
            text += l + "\n"

        await update.message.reply_text(text)

    except:

        await update.message.reply_text("❌ Ошибка поиска")


def main():

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN not set")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("jobs", jobs))

    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("🚀 BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
