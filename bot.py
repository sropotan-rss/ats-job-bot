```python
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from ai_engine import analyze_resume_vacancy
from vacancy_parser import parse_vacancy

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

resume_storage = {}

executor = ThreadPoolExecutor(max_workers=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Привет!\n\n"
        "1️⃣ Отправь резюме\n"
        "2️⃣ Затем отправь вакансию\n\n"
        "Я сделаю ATS анализ."
    )


async def progress_bar(message):

    progress_steps = [10, 25, 50, 75, 90]

    for p in progress_steps:
        await asyncio.sleep(2)
        try:
            await message.edit_text(f"🔎 Анализирую...\n\n{p}%")
        except:
            pass


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id
    text = update.message.text

    if user not in resume_storage:

        resume_storage[user] = text[:1500]

        await update.message.reply_text(
            "✅ Резюме сохранено\n\nТеперь отправь вакансию."
        )

        return

    vacancy = parse_vacancy(text)[:1500]
    resume = resume_storage[user]

    msg = await update.message.reply_text("🔎 Анализирую...\n\n0%")

    loop = asyncio.get_event_loop()

    progress_task = asyncio.create_task(progress_bar(msg))

    try:

        result = await loop.run_in_executor(
            executor,
            analyze_resume_vacancy,
            resume,
            vacancy
        )

        progress_task.cancel()

        await msg.edit_text(
            "✅ Анализ готов\n\n" + result
        )

    except Exception as e:

        logging.error(e)

        await msg.edit_text(
            "❌ Ошибка анализа"
        )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
```
