import logging
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import aiohttp  # استبدال requests بـ aiohttp

# إعدادات Firebase
cred = credentials.Certificate(r"C:\Users\LENOVO\Desktop\therapp\serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# إعدادات التليجرام
TELEGRAM_TOKEN = "7996338110:AAGKkgFy1qpUQG4E9A4ZJrgc0aon4cx8JpI"
HTML_PAGE_URL = "https://wednsdaychess.vercel.app"

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# الدالة التي ستتم عند استقبال الرسائل
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    username = user.username
    # البحث عن المستخدم في قاعدة البيانات
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()

    if doc.exists:
        # إذا كان المستخدم موجودًا بالفعل
        user_data = doc.to_dict()
        points = user_data.get("points", 0)
    else:
        # إذا كان المستخدم غير موجود
        points = 5  # إضافة 5 نقاط للمستخدم الجديد
        # إضافة المستخدم إلى قاعدة البيانات
        user_ref.set({
            'username': username,
            'points': points
        })

    # إرسال البيانات إلى صفحة HTML باستخدام aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(HTML_PAGE_URL, json={"username": username, "points": points}) as response:
            if response.status == 200:
                logger.info(f"Data sent successfully for {username}")
            else:
                logger.error(f"Failed to send data for {username}, status code: {response.status}")

    # رد التليجرام
    await update.message.reply_text(f"مرحبًا {username}!\nعدد النقاط: {points}")

# الدالة الرئيسية لتشغيل البوت
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    application.run_polling()

if __name__ == '__main__':
    main()
