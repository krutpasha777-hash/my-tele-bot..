import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- СЕРВЕР ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Live!'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))), daemon=True).start()

# --- БОТ ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "Бот готов! Жми кнопки или пришли фото списка запчастей.", reply_markup=markup)

# Обработка кнопки "Погода"
@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.reply_to(message, "🌤 В Днепре сейчас +5°C, облачно. (Это демо-режим)")

# Обработка кнопки "Заметки"
@bot.message_handler(func=lambda message: message.text == "Заметки")
def notes(message):
    bot.reply_to(message, "📝 Твои последние заметки пусты.")

# --- ГЛАВНОЕ: ОБРАБОТКА ФОТО ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "🔍 Вижу список! Читаю почерк...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Запрос к OCR API
        r = requests.post('https://api.ocr.space/parse/image', 
                          data={'url': file_url, 'apikey': 'helloworld', 'language': 'rus'})
        text = r.json()['ParsedResults'][0]['ParsedText']
        
        # Улучшенный поиск цен: ищем числа, которые стоят после знака "-" или в конце строки
        # Это поможет не считать "номер детали" как цену
        prices = re.findall(r'-\s*(\d+)', text) # ищет цифры после тире
        if not prices:
            prices = re.findall(r'(\d+)\s*$', text, re.MULTILINE) # или в конце строки
            
        total = sum(map(int, prices))
        
        res = f"📋 **Распознал:**\n{text[:300]}...\n\n"
        res += f"💰 **Итого по ценам:** {total} грн"
        bot.send_message(message.chat.id, res)
    except:
        bot.send_message(message.chat.id, "❌ Ошибка чтения. Попробуй фото почетче!")

# Ответ на любой другой текст
@bot.message_handler(func=lambda message: True)
def other(message):
    bot.reply_to(message, "Я тебя понял! Но лучше нажми кнопку или пришли фото.")

bot.polling(none_stop=True)
