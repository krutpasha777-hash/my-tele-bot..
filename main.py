import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- SERVER (ОБМАНКА ДЛЯ RENDER) ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Live!'

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

# --- BOT SETUP ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "✅ Бот настроен! Пришли фото списка или нажми кнопку.", reply_markup=markup)

# --- ОБРАБОТКА КНОПОК ---
@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.send_message(message.chat.id, "🌤 В Днепре сейчас облачно, около +5°C. Хорошего дня!")

@bot.message_handler(func=lambda message: message.text == "Итоги")
def summary(message):
    bot.send_message(message.chat.id, "📊 Здесь будет храниться сумма твоих заказов за месяц!")

# --- ОБРАБОТКА ФОТО (СПЕЦИАЛЬНО ДЛЯ ЗАПЧАСТЕЙ) ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "🔍 Вижу список! Разбираю почерк, ищу только цены...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Запрос к OCR API
        r = requests.post('https://api.ocr.space/parse/image', 
                          data={'url': file_url, 'apikey': 'helloworld', 'language': 'rus'})
        result = r.json()
        
        if result.get('OCRExitCode') == 1:
            detected_text = result['ParsedResults'][0]['ParsedText']
            
            # Улучшенный поиск: ищем числа, которые стоят после "-" или "+"
            # Это отсеет номера деталей (88, 109, 113) и возьмет только цены/кол-во
            prices = re.findall(r'[-+]\s*(\d+)', detected_text)
            
            # Если после знаков ничего нет, берем числа в конце строк
            if not prices:
                prices = re.findall(r'(\d+)(?:\s|$)', detected_text)

            total = sum(map(int, prices))
            
            report = f"📝 **Распознанный текст:**\n`{detected_text[:250]}...`\n\n"
            report += f"💰 **Насчитал (только цены):** {total} грн"
            bot.send_message(message.chat.id, report)
        else:
            bot.send_message(message.chat.id, "❌ Не смог разобрать. Попробуй сделать фото чуть ближе и при светe.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

# Универсальный ответ на текст
@bot.message_handler(func=lambda message: True)
def other(message):
    bot.reply_to(message, "Нажми кнопку или пришли фото списка запчастей! ⚙️")

bot.polling(none_stop=True)
