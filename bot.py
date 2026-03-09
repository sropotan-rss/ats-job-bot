import os

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from parser import parse_hh
from ats_engine import analyze


def load_resume():

    with open("resume.txt", "r", encoding="utf-8") as f:
        return f.read()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text

    if "hh.ru" not in url:

        await update.message.reply_text("Send hh.ru vacancy link")

        return

    await update.message.reply_text("Analyzing vacancy...")

    vacancy = parse_hh(url)

    resume = load_resume()

    result = analyze(resume, vacancy)

    await update.message.reply_text(result[:4000])


def main():

    token = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.run_polling()


if __name__ == "__main__":

    main()
