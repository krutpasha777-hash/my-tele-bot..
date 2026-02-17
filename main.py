import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Live with Private Key!'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))), daemon=True).start()

# --- НАСТРОЙКИ БОТА ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957" # Твой личный ключ активирован!

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "✅ Личный ключ активен! Присылай фото списка на белом листе.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.send_message(message.chat.id, "🌤 В Днепре сейчас облачно, около +5°C. Хорошего дня!")

# --- ОБРАБОТКА ФОТО ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚙️ Сканирую список личным ключом... Подожди пару секунд.")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Запрос к ИИ с использованием Engine 2
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
            
            # Находим все группы цифр
            raw_numbers = re.findall(r'\d+', text)
            
            # Фильтруем: берем числа от 1 до 500 (чтобы не считать лишние данные)
            prices = [int(n) for n in raw_numbers if 1 <= int(n) <= 500]
            
            total = sum(prices)
            
            response = f"📝 **Что я увидел на листе:**\n`{text}`\n\n"
            response += f"🔢 **Распознанные цены:** {', '.join(map(str, prices))}\n"
            response += f"💰 **ОБЩАЯ СУММА:** {total} грн"
            
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "❌ Не удалось разобрать текст. Проверь освещение!")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

bot.polling(none_stop=True)
