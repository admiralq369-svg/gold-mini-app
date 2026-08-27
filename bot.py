import os
import threading
from flask import Flask
import telebot

# 1. إنشاء سيرفر Flask وهمي لفتح المنفذ بسلام لـ Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# 2. كود البوت الأساسي
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 1084981493))

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت Gold Signals Pro 🏆\nيرجى استخدام التطبيق لإتمام الاشتراك، وعند إرسال صورة الإيصال سيتم تحويلها للإدارة فوراً.")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username or "لا يوجد معرف"
    
    caption = (
        f"🚨 **إشعار دفع جديد من مشترك!**\n\n"
        f"👤 الاسم: {user_name}\n"
        f"🔗 اليوزر: @{username}\n"
        f"🆔 المعرف (ID): `{user_id}`\n\n"
        f"💡 قم بمراجعة الإيصال وأرسل له كود التفعيل المناسب من التطبيق."
    )
    
    try:
        bot.forward_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(ADMIN_ID, caption, parse_mode="Markdown")
        bot.reply_to(message, "✅ تم استلام إيصال الدفع بنجاح وتحويله للإدارة للمراجعة. سيتم إرسال كود التفعيل قريباً!")
    except Exception as e:
        print(f"Error: {e}")

# 3. تشغيل السيرفر والبوت في نفس الوقت
if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.start()
    print("Bot is running securely...")
    bot.polling(none_stop=True)
