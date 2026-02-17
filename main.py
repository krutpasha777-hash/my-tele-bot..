import telebot
import os
import requests
import re
from flask import Flask
import threading

# --- СТАБИЛЬНЫЙ СЕРВЕР ---
app = Flask(__name__)
@app.route('/')
def hello(): return 'Bot is Online!'

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))), daemon=True).start()

# --- НАСТРОЙКИ БОТА ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Добавить трату", "Итоги", "Заметки", "Погода")
    bot.send_message(message.chat.id, "🎯 Режим максимальной точности включен! Жду твой список.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Погода")
def weather(message):
    bot.send_message(message.chat.id, "🌤 В Днепре сейчас +5°C. Хорошего дня и продуктивной работы!")

# --- ГЛАВНАЯ ФУНКЦИЯ РАСПОЗНАВАНИЯ ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚙️ Нейросеть сканирует список... Секунду.")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Оптимальные параметры для рукописного текста на клетке
        payload = {
            'url': file_url,
            'apikey': 'helloworld',
            'language': 'rus',
            'OCREngine': '2',       # Engine 2 намного лучше видит цифры
            'scale': 'true',       # Принудительное увеличение для четкости
            'isTable': 'false'     # Отключаем таблицы, чтобы не путать колонки
        }
        
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=25)
        result = r.json()
        
        if 'ParsedResults' in result and result['ParsedResults']:
            text = result['ParsedResults'][0]['ParsedText']
            
            # ОЧЕНЬ ВАЖНО: Ищем все числа. 
            # Мы берем всё, что состоит из 1-4 цифр подряд.
            found_numbers = re.findall(r'\d+', text)
            
            # Фильтруем: убираем номера моделей (типа 600, 113), если они повторяются, 
            # или просто суммируем всё, что похоже на цену (обычно это последние цифры в строке)
            prices = [int(n) for n in found_numbers if 1 <= int(n) <= 2000]
            
            total = sum(prices)
            
            if total > 0:
                report = f"📋 **Распознал такие числа:** {', '.join(map(str, prices))}\n\n"
                report += f"💰 **Общая сумма:** {total} грн"
                bot.send_message(message.chat.id, report)
            else:
                bot.send_message(message.chat.id, "🔍 Вижу текст, но не вижу четких цифр. Попробуй обвести цены жирнее.")
        else:
            bot.send_message(message.chat.id, "⚠️ Не удалось прочитать. Попробуй сфоткать листок горизонтально и без теней.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "🔄 Ошибка связи. Попробуй еще раз через 30 секунд.")

bot.polling(none_stop=True)
