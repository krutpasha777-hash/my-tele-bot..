import telebot
import os
import requests
import re
from flask import Flask
import threading
import time

# --- СЕРВЕР ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Accounting System Online'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

# --- НАСТРОЙКИ И ПРАЙС-ЛИСТ ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957"

# Твои расценки
PRICES = {
    'колесо 113': 40,
    'трак 88': 10,
    'башмак а2': 2,
    'колесо 600': 50,
    'палец 88': 7
}

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🏗 Система учета готова! Присылай фото списка, и я посчитаю зарплату за день.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "🔢 Считаю по прайсу...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        payload = {
            'url': file_url,
            'apikey': API_KEY,
            'language': 'rus',
            'OCREngine': '2',
            'scale': 'true'
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload)
        result = r.json()
        
        if 'ParsedResults' in result:
            text = result['ParsedResults'][0]['ParsedText'].lower()
            lines = text.split('\n')
            
            report = "📝 **ОТЧЕТ ПО РАБОТЕ:**\n\n"
            total_sum = 0
            found_anything = False

            for item, price in PRICES.items():
                if item in text:
                    # Ищем число после названия детали (например, "колесо 113 - 8")
                    pattern = rf"{item}.*?(\d+)"
                    match = re.search(pattern, text)
                    if match:
                        count = int(match.group(1))
                        cost = count * price
                        total_sum += cost
                        report += f"✅ {item.capitalize()}: {count} шт. × {price} = {cost} грн\n"
                        found_anything = True

            if found_anything:
                report += f"\n💰 **ИТОГО ЗА СЕГОДНЯ: {total_sum} грн**"
                report += f"\n📅 Дата: {time.strftime('%d.%m.%Y')}"
                bot.send_message(message.chat.id, report)
            else:
                bot.send_message(message.chat.id, f"🔍 Вижу текст: `{text}`, но не нашел деталей из прайса. Проверь названия!")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось прочитать список.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Ошибка. Попробуй еще раз через минуту.")

bot.remove_webhook()
bot.polling(none_stop=True)
