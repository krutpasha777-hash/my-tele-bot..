import telebot
import os
import time
import threading
import random
import re
from telebot import types
from flask import Flask # Добавили эту библиотеку

# --- МИНИ-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Bot is running!'

def run_flask():
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))

# Запускаем веб-сервер в отдельном потоке
threading.Thread(target=run_flask).start()
# -------------------------------------

TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN, threaded=False)

# ... (весь твой остальной код бота без изменений) ...
# Вставь сюда все функции: send_reminder, main_keyboard, start, 
# show_summary, weather, motivation, show_fin, show_not, clear_all, handle_all

# В самом конце оставь это:
print("--- БОТ ЗАПУЩЕН НА СЕРВЕРЕ ---")
import requests # Не забудь добавить это в начало файла к остальным import

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 Вижу фото! Пытаюсь распознать текст и посчитать сумму...")
    
    try:
        # Получаем ссылку на фото
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Используем бесплатный API для распознавания (OCR.space)
        # Мы используем их публичный ключ 'helloworld' для начала
        payload = {
            'url': file_url,
            'apikey': 'helloworld',
            'language': 'rus',
            'isOverlayRequired': False,
            'FileType': 'JPG',
        }
        r = requests.post('https://api.ocr.space/parse/image', data=payload)
        result = r.json()
        
        if result['OCRExitCode'] == 1:
            detected_text = result['ParsedResults'][0]['ParsedText']
            # Ищем все числа (цены) в тексте
            prices = re.findall(r'\d+', detected_text)
            total = sum(map(int, prices))
            
            response = f"✅ Распознанный текст:\n\n{detected_text}\n"
            response += f"--- \n🧮 Сумма всех найденных чисел: {total}"
            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "❌ Не удалось прочитать текст на фото.")
            
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {e}")
while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=20)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)
