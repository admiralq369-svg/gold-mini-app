import os
import threading
from flask import Flask
import telebot
from supabase import create_client, Client

# 1. إعداد سيرفر Flask للحفاظ على عمل البوت في Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# 2. إعداد المتغيرات والاتصال بـ Supabase
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = telebot.TeleBot(TOKEN)

# 3. أوامر البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "أهلاً بك! يرجى إرسال كود التفعيل الخاص بك لتفعيل الاشتراك."
    )

@bot.message_handler(func=lambda message: True)
def handle_activation(message):
    user_id = message.from_user.id
    input_code = message.text.strip()

    try:
        # البحث عن الكود في جدول Supabase
        response = supabase.table('activation_codes') \
            .select('*') \
            .eq('code', input_code) \
            .execute()
        
        codes = response.data

        if not codes:
            bot.reply_to(message, "❌ هذا الكود غير صحيح، يرجى التأكد وإعادة المحاولة.")
            return

        code_data = codes[0]

        if code_data.get('is_used'):
            bot.reply_to(message, "⚠️ هذا الكود تم استخدامه من قبل وغير صالح للان الاستخدام.")
            return

        # تحديث الكود ليصبح مستخدماً وربطه بـ user_id
        supabase.table('activation_codes') \
            .update({'is_used': True, 'user_id': user_id}) \
            .eq('code', input_code) \
            .execute()

        bot.reply_to(message, "✅ تم تفعيل اشتراكك بنجاح! مرحباً بك معنا.")

    except Exception as e:
        bot.reply_to(message, "حدث خطأ أثناء التفعيل، يرجى المحاولة لاحقاً.")

# 4. تشغيل السيرفر والبوت
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
