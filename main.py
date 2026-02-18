import telebot
import requests
import re
import time

# --- НАСТРОЙКИ ---
TOKEN = "8239395932:AAGtE84FBa8OzFcUfNSAiOES9xa8jYpNWqY"
API_KEY = "K84042405788957"

# Упрощенный прайс (только ключевые слова)
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
    bot.send_message(message.chat.id, "✅ Гриша готов к работе! Кидай фото списка.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    msg = bot.reply_to(message, "⏳ Читаю текст... Подожди секунд 30.")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        # Запрос к OCR (быстрый движок)
        payload = {'url': file_url, 'apikey': API_KEY, 'language': 'rus', 'OCREngine': '1'}
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=30)
        result = r.json()
        
        if 'ParsedResults' in result:
            text = result['ParsedResults'][0]['ParsedText'].lower()
            
            report = "📝 **ОТЧЕТ:**\n\n"
            total = 0
            
            # Простой поиск по строкам
            for item, price in PRICES.items():
                if item in text:
                    # Ищем число в строке с деталью
                    match = re.search(rf"{item}.*?(\d+)", text)
                    if match:
                        count = int(match.group(1))
                        # Если это номер модели, ищем второе число
                        if count in [113, 88, 600]:
                            nums = re.findall(r'\d+', text.split(item)[1])
                            count = int(nums[1]) if len(nums) > 1 else count
                        
                        summa = count * price
                        total += summa
                        report += f"• {item.upper()}: {count} шт. = {summa} грн\n"

            if total > 0:
                report += f"\n💰 **ИТОГО: {total} грн**"
                bot.edit_message_text(report, chat_id=message.chat.id, message_id=msg.message_id)
            else:
                bot.send_message(message.chat.id, f"🔍 Текст увидел, но детали из прайса не нашел. Увидел:\n`{text}`")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось расшифровать фото. Попробуй еще раз.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Сервер перегружен. Попробуй через минуту.")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling(none_stop=True)
