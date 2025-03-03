import os
import telebot
import openai
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Берем токены из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация бота и OpenAI
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

# Промпт для ChatGPT
PROMPT = """Запрос 1
Представь, что ты специалист по распаковке личности, а я твой Клиент...
Твоя задача — получить от Клиента информацию, необходимую для составления уникального контент-плана.
Задавай вопросы по одному, уточняй, получай ответы и только тогда переходи к следующему вопросу.
Запрос 2
Проведи на основе распаковки маркетинговый анализ целевой аудитории...
"""

@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Я бот для распаковки личности. Напиши мне что-нибудь!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

# Запуск бота
bot.polling(none_stop=True)
