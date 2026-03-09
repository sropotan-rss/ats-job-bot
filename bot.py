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

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

user_state = {}

# =========================
# МЕНЮ
# =========================

def main_menu():

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("📊 Анализ резюме")
    kb.add("✨ Улучшить резюме")
    kb.add("✉️ Cover letter")
    kb.add("💰 Оценка зарплаты")

    return kb


# =========================
# СТАРТ
# =========================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    await message.answer(
        "🤖 ULTRA AI HR BOT\n\n"
        "Я могу:\n"
        "• анализировать резюме\n"
        "• улучшать резюме\n"
        "• писать cover letter\n"
        "• оценивать зарплату\n",
        reply_markup=main_menu()
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
# ПОЛУЧЕНИЕ ФАЙЛА
# =========================

async def extract_text(message):

    uid = message.from_user.id

    if message.document:

        file = await bot.get_file(message.document.file_id)

        path = f"file_{uid}"

        await message.document.download(destination_file=path)

        if message.document.file_name.endswith(".pdf"):
            return read_pdf(path)

        elif message.document.file_name.endswith(".docx"):
            return read_docx(path)

    return message.text


# =========================
# АНАЛИЗ
# =========================

@dp.message_handler(lambda m: m.text == "📊 Анализ резюме")
async def analyze_start(message: types.Message):

    user_state[message.from_user.id] = {"mode": "analysis", "step": "resume"}

    await message.answer("📄 Отправьте резюме")


# =========================
# УЛУЧШЕНИЕ
# =========================

@dp.message_handler(lambda m: m.text == "✨ Улучшить резюме")
async def improve_resume(message: types.Message):

    user_state[message.from_user.id] = {"mode": "improve"}

    await message.answer("📄 Отправьте резюме")


# =========================
# COVER LETTER
# =========================

@dp.message_handler(lambda m: m.text == "✉️ Cover letter")
async def cover_letter(message: types.Message):

    user_state[message.from_user.id] = {"mode": "cover"}

    await message.answer("📄 Отправьте резюме")


# =========================
# ЗАРПЛАТА
# =========================

@dp.message_handler(lambda m: m.text == "💰 Оценка зарплаты")
async def salary(message: types.Message):

    user_state[message.from_user.id] = {"mode": "salary"}

    await message.answer("📄 Отправьте резюме")


# =========================
# ОБРАБОТКА
# =========================

@dp.message_handler(content_types=["text", "document"])
async def process(message: types.Message):

    uid = message.from_user.id

    if uid not in user_state:
        return

    text = await extract_text(message)

    mode = user_state[uid]["mode"]

    msg = await message.answer("🔍 AI анализирует... 10%")

    await asyncio.sleep(1)
    await msg.edit_text("🧠 Обработка навыков... 40%")

    result = await ai_request(text, mode)

    await msg.edit_text("📊 Формирую отчёт... 90%")

    await asyncio.sleep(1)

    await msg.edit_text(result)

    del user_state[uid]


# =========================
# AI
# =========================

async def ai_request(text, mode):

    prompts = {

        "analysis": f"""
Ты HR специалист.

Проанализируй резюме.

{text}

Ответь:

Процент совпадения
ATS score
Сильные стороны
Недостающие навыки
Шанс получить интервью
""",

        "improve": f"""
Улучши резюме:

{text}

Сделай его более сильным для работодателя.
""",

        "cover": f"""
Напиши сильное cover letter на основе резюме:

{text}
""",

        "salary": f"""
Оцени возможную зарплату кандидата на основе резюме:

{text}

Ответь диапазоном.
"""
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    json_data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompts[mode]}
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

                return data["choices"][0]["message"]["content"]

    except Exception as e:

        print(e)

        return "❌ Ошибка AI"


# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
