import openai
import telebot
import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Получаем API-ключи из переменных окружения
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

# Начальный промт для интервью
initial_prompt = """Запрос 1
Представь, что ты специалист по распаковке личности, а я твой Клиент - <!EXPERT_OF>
:: Твоя задача — получить от Клиента информацию, необходимую для составления уникального контент-плана 
:: Задавай вопросы по одному в формате интервью 
:: постарайся получить максимум информации о ценностях Клиента, его отношении к своей профессии, личных увлечениях, чертах личности, сообщениях, которые он несет аудитории, какой свой образ хочет создать у аудитории.
Задавай вопросы по одному, уточняй, получай ответы и только тогда задавай второй вопрос из списка.
"""

# Промт для анализа ЦА
audience_analysis_prompt = """Запрос 2
Проведи на основе распаковки маркетинговый анализ целевой аудитории. Выдели 3 основных сегмента целевой аудитории на основе данных выше и опиши по очереди их характеристики по пунктам, сначала для первого сегмента, потом второго и третьего, по отдельности:
- Социально-демографические данные
- Интересы
- Потребности
- Платежеспособность
- Поведенческие факторы
- Ценности
- Образ жизни, хобби и интересы
- 3 боли
- 3 возражения
- 3 драйвера к покупке
- Подбери мероприятия, которые мои клиенты чаще всего посещают
"""

# Состояние беседы
user_sessions = {}

@bot.message_handler(commands=['start'])
def start_conversation(message):
    user_id = message.chat.id
    user_sessions[user_id] = []  # Храним диалог
    bot.send_message(user_id, "Привет! Я помогу тебе с распаковкой личности. Давай начнем!")
    ask_next_question(user_id, initial_prompt)

def ask_next_question(user_id, context):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": context}]
    )
    question = response['choices'][0]['message']['content']
    user_sessions[user_id].append({"role": "assistant", "content": question})
    bot.send_message(user_id, question)

@bot.message_handler(func=lambda message: message.chat.id in user_sessions)
def handle_response(message):
    user_id = message.chat.id
    user_sessions[user_id].append({"role": "user", "content": message.text})
    
    # Если пользователь вводит "/analyze", переключаемся на анализ ЦА
    if message.text.lower() == "/analyze":
        analyze_audience(user_id)
    else:
        ask_next_question(user_id, message.text)

def analyze_audience(user_id):
    context = "\n".join([msg["content"] for msg in user_sessions[user_id]])
    full_prompt = context + "\n\n" + audience_analysis_prompt
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": full_prompt}]
    )
    
    analysis = response['choices'][0]['message']['content']
    bot.send_message(user_id, "🔍 Анализ целевой аудитории:\n" + analysis)

# Запуск бота
bot.polling()