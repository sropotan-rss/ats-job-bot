import logging
import asyncio
import aiohttp
import pdfplumber
import docx

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils import executor

# =========================
# НАСТРОЙКИ
# =========================

TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
GROQ_API_KEY = "YOUR_GROQ_API_KEY"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# =========================
# ЛОГИ
# =========================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# =========================
# ХРАНЕНИЕ
# =========================

user_state = {}

# =========================
# МЕНЮ
# =========================

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📄 Анализ резюме")
    kb.add("ℹ️ Помощь")
    return kb


# =========================
# СТАРТ
# =========================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    await message.answer(
        "🤖 AI HR бот\n\n"
        "Я могу проанализировать резюме относительно вакансии.",
        reply_markup=main_menu()
    )


# =========================
# ПОМОЩЬ
# =========================

@dp.message_handler(lambda m: m.text == "ℹ️ Помощь")
async def help_cmd(message: types.Message):

    await message.answer(
        "📌 Как пользоваться:\n\n"
        "1️⃣ Нажмите *Анализ резюме*\n"
        "2️⃣ Отправьте резюме\n"
        "3️⃣ Отправьте вакансию\n\n"
        "Поддерживаются:\n"
        "TXT\nPDF\nDOCX",
        parse_mode="Markdown"
    )


# =========================
# НАЧАТЬ АНАЛИЗ
# =========================

@dp.message_handler(lambda m: m.text == "📄 Анализ резюме")
async def start_analysis(message: types.Message):

    user_state[message.from_user.id] = {"step": "resume"}

    await message.answer(
        "📄 Отправьте резюме\n\n"
        "Можно:\n"
        "TXT\nPDF\nDOCX"
    )


# =========================
# ЧТЕНИЕ PDF
# =========================

def read_pdf(path):

    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    return text


# =========================
# ЧТЕНИЕ DOCX
# =========================

def read_docx(path):

    doc = docx.Document(path)

    text = "\n".join(p.text for p in doc.paragraphs)

    return text


# =========================
# ПОЛУЧЕНИЕ РЕЗЮМЕ
# =========================

@dp.message_handler(content_types=["document", "text"])
async def receive_resume(message: types.Message):

    uid = message.from_user.id

    if uid not in user_state:
        return

    if user_state[uid]["step"] != "resume":
        return

    if message.document:

        file = await bot.get_file(message.document.file_id)
        path = f"resume_{uid}"

        await message.document.download(destination_file=path)

        if message.document.file_name.endswith(".pdf"):
            text = read_pdf(path)

        elif message.document.file_name.endswith(".docx"):
            text = read_docx(path)

        else:
            await message.answer("❌ Поддерживаются только PDF или DOCX")
            return

    else:

        text = message.text

    user_state[uid]["resume"] = text
    user_state[uid]["step"] = "vacancy"

    await message.answer("📋 Теперь отправьте текст вакансии")


# =========================
# ПОЛУЧЕНИЕ ВАКАНСИИ
# =========================

@dp.message_handler()
async def receive_vacancy(message: types.Message):

    uid = message.from_user.id

    if uid not in user_state:
        return

    if user_state[uid]["step"] != "vacancy":
        return

    user_state[uid]["vacancy"] = message.text

    resume = user_state[uid]["resume"]
    vacancy = user_state[uid]["vacancy"]

    msg = await message.answer("🔍 Анализирую резюме... 10%")

    await asyncio.sleep(1)
    await msg.edit_text("🔍 Анализирую навыки... 40%")

    result = await analyze_ai(resume, vacancy)

    await msg.edit_text("🔍 Формирую отчёт... 90%")

    await asyncio.sleep(1)

    await msg.edit_text(result)

    del user_state[uid]


# =========================
# AI
# =========================

async def analyze_ai(resume, vacancy):

    prompt = f"""
Ты HR специалист.

Проанализируй резюме относительно вакансии.

Резюме:
{resume}

Вакансия:
{vacancy}

Ответь структурировано:

Процент совпадения: %

Подходит ли кандидат

Сильные стороны

Недостающие навыки

Советы кандидату
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    json_data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:

        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:

            async with session.post(
                GROQ_URL,
                headers=headers,
                json=json_data
            ) as resp:

                data = await resp.json()

                if "choices" not in data:
                    return "⚠️ AI не ответил"

                return data["choices"][0]["message"]["content"]

    except Exception as e:

        print(e)

        return "❌ Ошибка AI сервиса"


# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
