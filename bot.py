```python
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ai_engine import analyze_resume_vacancy
from vacancy_parser import parse_vacancy

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

resume_storage = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Отправь своё резюме текстом.\n"
        "После этого отправь вакансию — я скажу, насколько ты подходишь."
    )

# обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id
    text = update.message.text

    # если резюме ещё нет — сохраняем
    if user not in resume_storage:
        resume_storage[user] = text[:3000]  # обрезка длинного текста
        await update.message.reply_text(
            "✅ Резюме сохранено.\n\nТеперь отправь вакансию."
        )
        return

    # если резюме уже есть — считаем это вакансией
    vacancy = parse_vacancy(text)[:3000]
    resume = resume_storage[user]

    msg = await update.message.reply_text("🔎 Анализирую...")

    try:
        result = analyze_resume_vacancy(resume, vacancy)

        await msg.edit_text(
            "📊 Результат анализа:\n\n" + result
        )

    except Exception as e:
        logging.error(e)
        await msg.edit_text(
            "❌ Ошибка анализа. Попробуй ещё раз."
        )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()
```
