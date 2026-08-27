import os
import threading
from flask import Flask
import telebot
from supabase import create_client, Client

# 1. إعداد سيرفر Flask لإبقاء الخدمة نشطة على Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# 2. إعداد الاتصال وربط المتغيرات
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID', '0')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = telebot.TeleBot(TOKEN)

# 3. أمر البدء /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت تفعيل اشتراكات الذهب. يرجى إرسال كود التفعيل الخاص بك هنا لتفعيل اشتراكك فوراً.")

# 4. استقبال الصور (إيصالات الدفع) وإرسالها للأدمن
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        user = message.from_user
        caption = f"🚨 إشعار دفع جديد من مشترك!\n\nالاسم: {user.first_name}\nاليوزر: @{user.username if user.username else 'لا يوجد'}\nالمعرف (ID): `{user.id}`"
        
        # إعادة توجيه الصورة للأدمن إذا تم ضبطه
        if ADMIN_ID != '0':
            bot.send_photo(int(ADMIN_ID), message.photo[-1].file_id, caption=caption, parse_mode="Markdown")
        
        bot.reply_to(message, "✅ تم استلام صورة الإيصال بنجاح وإرسالها للمراجعة. سيتم تفعيل حسابك قريباً.")
    except Exception as e:
        print(f"Photo Error: {e}")
        bot.reply_to(message, "حدث خطأ أثناء إرسال الصورة، يرجى المحاولة لاحقاً.")

# 5. معالجة النصوص (أكواد التفعيل مثل Test123) بصورة صريحة
@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def handle_activation(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or ""
    input_code = message.text.strip()
    
    try:
        # البحث عن الكود في جدول activation_codes
        response = supabase.table("activation_codes").select("*").eq("code", input_code).execute()
        codes = response.data
        
        if not codes:
            bot.reply_to(message, "❌ كود التفعيل غير صحيح، يرجى التحقق وإعادة المحاولة.")
            return
            
        code_data = codes[0]
        
        if code_data.get('is_used'):
            bot.reply_to(message, "⚠️ عذراً، هذا الكود مستخدم مسبقاً.")
            return
            
        # تحديث الكود كمستخدم
        supabase.table("activation_codes").update({"is_used": True, "used_by": user_id}).eq("code", input_code).execute()
        
        # حفظ أو تحديث الاشتراك في جدول subscriptions
        supabase.table("subscriptions").upsert({
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "status": "active"
        }).execute()
        
        bot.reply_to(message, "✅ تم تفعيل اشتراكك بنجاح! أهلاً بك في القناة المدفوعة.")
        
    except Exception as e:
        error_msg = str(e)
        print(f"Activation Error: {error_msg}")
        bot.reply_to(message, f"⚠️ خطأ تقني في قاعدة البيانات:\n{error_msg}")

# 6. التشغيل المتزامن للبوت والسيرفر
if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    
    print("Bot is running...")
    bot.infinity_polling()
