import os

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from parser import parse_hh
from ats_engine import analyze


def load_resume():
    with open("resume.txt", "r", encoding="utf-8") as f:
        return f.read()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    url = update.message.text

    if "hh.ru" not in url:
        await update.message.reply_text("Send hh.ru vacancy link")
        return

    await update.message.reply_text("Analyzing vacancy...")

    try:
        vacancy = parse_hh(url)
        resume = load_resume()

        result = analyze(resume, vacancy)

        await update.message.reply_text(result[:4000])

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


def main():

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN not set")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
