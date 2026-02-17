import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- SERVER ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Online!'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))), daemon=True).start()

# --- BOT SETUP ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "🎯 Режим максимальной точности включен! Жду фото твоего списка.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.send_message(message.chat.id, "🌤 В Днепре сейчас облачно, +5°C. Удачного ремонта!")

# --- ГЛАВНАЯ ФУНКЦИЯ РАСПОЗНАВАНИЯ ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚙️ Нейросеть сканирует список... Секунду.")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Настройки для Engine 2 (лучший для рукописных цифр)
        payload = {
            'url': file_url,
            'apikey': 'K87871923388957',
            'language': 'rus',
            'OCREngine': '2',
            'scale': 'true' # Увеличивает фото для лучшего чтения
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=25)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText']
            
            # Ищем все числа от 5 до 5000 (чтобы не путать с мелкими точками)
            all_nums = re.findall(r'\d+', text)
            prices = [int(n) for n in all_nums if 5 <= int(n) <= 5000]
            
            total = sum(prices)
            
            if total > 0:
                # Показываем, какие цифры ИИ смог "увидеть"
                res = f"📝 **Я нашел в списке цифры:** {', '.join(map(str, prices))}\n"
                res += f"💰 **Итого:** {total} грн"
                bot.send_message(message.chat.id, res)
            else:
                bot.send_message(message.chat.id, "🔍 Вижу текст, но не нашел в нем четких сумм. Попробуй обвести цены жирнее.")
        else:
            bot.send_message(message.chat.id, "⚠️ Не удалось разобрать. Попробуй сфоткать листок ровнее.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Ошибка связи. Попробуй еще раз через 30 секунд.")

bot.polling(none_stop=True)
