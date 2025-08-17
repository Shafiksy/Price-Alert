import telegram
from telegram.ext import ApplicationBuilder, CallbackContext
import requests
import time
import logging

# --- الإعدادات الأساسية ---
TOKEN = "7549834229:AAEg5jZsfaZ8ZyBXww7ygz625RjrVz97zXc"
CHANNEL_ID = "@SaharaUSD"
COIN_ID = "sahara-ai"
COIN_SYMBOL = "SAHARA"
UPDATE_INTERVAL_SECONDS = 30

# متغير عالمي لتخزين السعر الأخير للمقارنة
last_price = 0

# إعداد تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- وظيفة جلب السعر (تبقى كما هي) ---
def get_crypto_price(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url )
        response.raise_for_status()
        data = response.json()
        price = data[coin_id]['usd']
        return price
    except Exception as e:
        logger.error(f"خطأ في جلب السعر: {e}")
        return None

# --- وظيفة إرسال الرسالة (تم تعديلها بالكامل) ---
# --- وظيفة إرسال الرسالة (تم تعديلها لتكون أبسط) ---
async def send_price_update(context: CallbackContext):
    global last_price  # نستخدم المتغير العالمي
    
    logger.info("البدء في جلب تحديث السعر...")
    
    job_data = context.job.data
    current_price = get_crypto_price(job_data['coin_id'])
    
    if current_price is not None:
        # تحديد الإيموجي بناءً على مقارنة الأسعار
        if last_price == 0:
            emoji = "🌚"
        elif current_price > last_price:
            emoji = "🟢"
        elif current_price < last_price:
            emoji = "🔴"
        else:
            emoji = "🌚"

        # تحديث السعر الأخير
        last_price = current_price
        
        # --- تنسيق الرسالة الجديد (المطلوب) ---
        # الرسالة تحتوي فقط على الإيموجي والسعر داخل وسم <code>
        message = f"{emoji} <code>${current_price:,.8f}</code>"
        
        logger.info(f"تم جلب السعر، الرسالة الجديدة: {message}")
        try:
            # إرسال الرسالة مع تفعيل وضع HTML
            await context.bot.send_message(
                chat_id=job_data['channel_id'], 
                text=message, 
                parse_mode='HTML'
            )
            logger.info(f"تم إرسال التحديث بنجاح إلى القناة.")
        except Exception as e:
            logger.error(f"فشل إرسال الرسالة إلى تليغرام: {e}")
    else:
        logger.warning("لم يتم جلب السعر، تخطي هذا التحديث.")

# --- الدالة الرئيسية (تبقى كما هي) ---
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    job_data = {
        'channel_id': CHANNEL_ID,
        'coin_id': COIN_ID,
        'coin_symbol': COIN_SYMBOL
    }
    
    application.job_queue.run_repeating(
        send_price_update, 
        interval=UPDATE_INTERVAL_SECONDS, 
        first=5,
        data=job_data
    )

    print("=============================================")
    print(f"تم تشغيل البوت بنجاح (مع تحسينات!)")
    print(f"القناة المستهدفة: {CHANNEL_ID}")
    print(f"سيتم إرسال تحديث كل {UPDATE_INTERVAL_SECONDS} ثانية.")
    print("=============================================")
    
    application.run_polling()

if __name__ == '__main__':
    main()
