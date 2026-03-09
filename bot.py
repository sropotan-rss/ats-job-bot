import os

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

from parser import parse_hh
from ats_engine import analyze
from resume_reader import read_pdf
from hh_search import search_jobs


resume_text = ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

        "Send PDF resume\n"
        "Send hh.ru vacancy link\n"
        "Command: /jobs Product Manager"

    )


async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global resume_text

    file = await update.message.document.get_file()

    path = "resume.pdf"

    await file.download_to_drive(path)

    resume_text = read_pdf(path)

    await update.message.reply_text("Resume uploaded")


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global resume_text

    if not update.message:
        return

    url = update.message.text

    if "hh.ru" not in url:

        await update.message.reply_text("Send hh.ru vacancy link")

        return

    if not resume_text:

        with open("resume.txt", "r", encoding="utf-8") as f:

            resume_text = f.read()

    await update.message.reply_text("Analyzing vacancy...")

    vacancy = parse_hh(url)

    result = analyze(resume_text, vacancy)

    await update.message.reply_text(result[:4000])


async def jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = " ".join(context.args)

    if not query:

        await update.message.reply_text("Example: /jobs Product Manager")

        return

    links = search_jobs(query)

    text = "Top vacancies:\n\n"

    for l in links:

        text += l + "\n"

    await update.message.reply_text(text)


def main():

    token = os.getenv("BOT_TOKEN")

    if not token:

        raise ValueError("BOT_TOKEN not set")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("jobs", jobs))

    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":

    main()
