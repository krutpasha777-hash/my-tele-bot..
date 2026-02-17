import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- SERVER FOR RENDER ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is running!'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))), daemon=True).start()

# --- BOT SETUP ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "🚀 Супер-глаз активирован! Пришли фото списка, я очень постараюсь посчитать.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.send_message(message.chat.id, "🌤 В Днепре сейчас +5°C. Хорошего дня!")

# --- ГЛАВНАЯ МАГИЯ: ОБРАБОТКА ФОТО ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚙️ Обрабатываю фото нейросетью... Это может занять до 10 секунд.")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Меняем настройки на Engine 2 и отключаем ориентацию (это ускоряет и улучшает чтение цифр)
        payload = {
            'url': file_url,
            'apikey': 'helloworld',
            'language': 'rus',
            'isOverlayRequired': False,
            'OCREngine': '2', # Второй движок лучше для цифр
            'scale': True     # Увеличивает фото перед чтением
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=20)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText']
            
            # Находим все группы цифр
            # Ищем числа от 5 до 5000 (чтобы не считать мелкие помарки)
            all_nums = re.findall(r'\d+', text)
            prices = [int(n) for n in all_nums if 5 <= int(n) <= 5000]
            
            total = sum(prices)
            
            if total > 0:
                res = f"📝 **Я увидел такие цифры:** {', '.join(map(str, prices))}\n"
                res += f"💰 **Итого:** {total} грн"
                bot.send_message(message.chat.id, res)
            else:
                bot.send_message(message.chat.id, "🔍 Текст вижу, но суммы не нашел. Напиши цены четче через тире.")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось прочитать. Попробуй сфоткать строго сверху и без теней.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Ошибка связи. Попробуй еще раз через минуту.")

bot.polling(none_stop=True)
