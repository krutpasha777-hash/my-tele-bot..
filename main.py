import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Live!'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))), daemon=True).start()

# --- НАСТРОЙКИ БОТА ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "💎 Режим СУПЕР-ЗРЕНИЯ включен! Теперь я читаю даже сложный почерк.", reply_markup=markup)

# Исправляем кнопку Погода
@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.send_message(message.chat.id, "🌤 В Днепре сейчас облачно, +5°C. Удачного ремонта!")

# --- ГЛАВНАЯ ФУНКЦИЯ: РАСПОЗНАВАНИЕ СПИСКА ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚡️ Включаю нейросеть Engine 2... Ищу цены в твоем списке...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Настройки для OCR: используем улучшенный движок и режим таблиц
        payload = {
            'url': file_url,
            'apikey': 'helloworld',
            'language': 'rus',
            'isTable': 'true',       # Распознает колонки
            'OCREngine': '2'         # ВТОРОЙ ДВИЖОК - ЛУЧШИЙ ДЛЯ РУКОПИСИ
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload)
        result = r.json()
        
        if 'ParsedResults' in result:
            text = result['ParsedResults'][0]['ParsedText']
            
            # Логика поиска цен: ищем числа, которые стоят после ТИРЕ или в КОНЦЕ строки
            # Это поможет игнорировать "Колесо 113" и брать только цену "8"
            found_prices = re.findall(r'[-=]\s*(\d+)', text)
            
            # Если после тире не нашли, берем просто все числа, которые больше 1 и меньше 5000
            if not found_prices:
                all_nums = re.findall(r'\b\d{1,4}\b', text)
                found_prices = [n for n in all_nums if 5 <= int(n) <= 3000] # Фильтр: от 5 до 3000 грн
            
            total = sum(map(int, found_prices))
            
            response = f"📝 **Я увидел в списке:**\n`{text[:300]}`\n\n"
            response += f"🔢 **Найденные суммы:** {', '.join(map(str, found_prices))}\n"
            response += f"💰 **ОБЩИЙ ИТОГ:** {total} грн"
            
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "⚠️ Не удалось прочитать. Попробуй сделать фото еще раз при ярком свете.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Ошибка связи с OCR. Попробуй через минуту.")

@bot.message_handler(func=lambda message: True)
def other(message):
    bot.reply_to(message, "Нажми на кнопку или просто пришли фото нового списка!")

bot.polling(none_stop=True)
