import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- СЕРВЕР ДЛЯ ПОДДЕРЖАНИЯ ЖИЗНИ БОТА ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Online and Ready!'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))), daemon=True).start()

# --- НАСТРОЙКИ БОТА ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
# ТВОЙ НОВЫЙ ЛИЧНЫЙ КЛЮЧ:
API_KEY = "K84042405788957" 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "🎯 Личный ключ активирован! Теперь я вижу идеально. Присылай фото списка.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.send_message(message.chat.id, "🌤 В Днепре сейчас облачно, +5°C. Удачного дня!")

# --- ОБРАБОТКА ФОТО ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚡️ Использую твой личный ключ для сканирования...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Настройки для Engine 2 (лучший для рукописи)
        payload = {
            'url': file_url,
            'apikey': API_KEY,
            'language': 'rus',
            'OCREngine': '2', 
            'scale': 'true'
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText']
            
            # Находим все числа от 1 до 500
            nums = re.findall(r'\d+', text)
            prices = [int(n) for n in nums if 1 <= int(n) <= 500]
            
            total = sum(prices)
            
            if total > 0:
                report = f"✅ **Я увидел в списке:**\n`{text}`\n\n"
                report += f"💰 **Итого насчитал:** {total} грн"
                bot.send_message(message.chat.id, report)
            else:
                bot.send_message(message.chat.id, "🔍 Текст вижу, но цены не распознал. Попробуй обвести их четче.")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка сервера: {result.get('ErrorMessage', 'Попробуй еще раз')}")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка связи: {e}")

bot.polling(none_stop=True)
