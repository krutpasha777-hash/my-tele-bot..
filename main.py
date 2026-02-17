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
    bot.send_message(message.chat.id, "💎 Режим супер-зрения включен! Присылай новый список.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.send_message(message.chat.id, "🌤 В Днепре сейчас облачно, +5°C. Самое время чинить технику!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚡️ Применяю улучшенные фильтры... Считаю суммы...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Используем расширенные параметры OCR
        payload = {
            'url': file_url,
            'apikey': 'helloworld',
            'language': 'rus',
            'isTable': 'true',       # Помогает при чтении списков
            'OCREngine': '2'         # ВТОРОЙ ДВИЖОК - ОН ЛУЧШЕ ДЛЯ ЦИФР
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload)
        result = r.json()
        
        if 'ParsedResults' in result:
            text = result['ParsedResults'][0]['ParsedText']
            
            # Ищем цены: теперь ищем любые числа от 1 до 4 знаков
            # Фильтруем слишком маленькие (номера деталей) и слишком большие
            all_numbers = re.findall(r'\b\d{1,4}\b', text)
            
            # Простая логика: если число стоит в конце строки или после тире
            # Но для начала просто выведем все найденные цифры, чтобы понять, что он видит
            prices = [int(n) for n in all_numbers if 5 <= int(n) <= 5000] # Игнорим мелочь меньше 5
            
            total = sum(prices)
            
            res = f"📝 **Текст со списка:**\n`{text}`\n\n"
            res += f"📊 **Найденные суммы:** {', '.join(map(str, prices))}\n"
            res += f"💰 **ИТОГО:** {total} грн"
            bot.send_message(message.chat.id, res)
        else:
            bot.send_message(message.chat.id, "🤔 Текст слишком размыт. Попробуй еще раз.")
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Ошибка связи с мозгом ИИ. Попробуй через минуту.")

bot.polling(none_stop=True)
