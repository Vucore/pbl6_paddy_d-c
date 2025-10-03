from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os
import base64
from io import BytesIO
import requests
from enum import Enum
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()
TOKEN_TELE = os.getenv("TOKEN_TELE")
API_URL = "http://localhost:8000/predict" 

# Lưu lựa chọn mô hình của người dùng
user_model_choices = {}
user_confidence_settings = {}  # Thêm dictionary lưu confidence

class ModelType(str, Enum):
    convit = "Mô hình ConVit"
    yolo = "Mô hình YOLO"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Tôi là Chatbot nhận diện bệnh lúa 🌾\n"
        "Bạn có thể sử dụng các lệnh sau:\n"
        "/select - Chọn mô hình dự đoán\n"
        "/conf - Điều chỉnh độ tin cậy (0.1-0.9)\n"
        "/upload - Tải ảnh lên để phân tích"
    )

async def select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Mô hình CNN"],
        ["Mô hình ConVit"],
        ["Mô hình YOLO"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Vui lòng chọn mô hình dự đoán:",
        reply_markup=reply_markup
    )

# Thêm command handler cho confidence
async def set_confidence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if context.args:
        try:
            conf_value = float(context.args[0])
            if 0.1 <= conf_value <= 0.9:
                user_confidence_settings[user_id] = conf_value
                await update.message.reply_text(
                    f"✅ Đã cài đặt độ tin cậy: {conf_value}"
                    "\n🖼 Bây giờ hãy gửi ảnh bệnh lúa của bạn bằng lệnh /upload"
                    "\nℹ️ Nếu chưa chọn mô hình, hãy sử dụng lệnh /select"
                )
            else:
                await update.message.reply_text(
                    "⚠️ Độ tin cậy phải từ 0.1 đến 0.9\n"
                    "Ví dụ: /conf 0.5"
                )
        except ValueError:
            await update.message.reply_text(
                "⚠️ Vui lòng nhập số hợp lệ\n"
                "Ví dụ: /conf 0.5"
            )
    else:
        current_conf = user_confidence_settings.get(user_id, 0.4)
        await update.message.reply_text(
            f"📊 Độ tin cậy hiện tại: {current_conf}\n"
            "Để thay đổi: /conf <giá trị>\n"
            "Ví dụ: /conf 0.5"
        )

async def handle_model_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    model_choice = update.message.text
    
    # Kiểm tra xem lựa chọn có hợp lệ không
    valid_models = [ModelType.convit, ModelType.yolo]
    if model_choice not in valid_models:
        await update.message.reply_text(
            "⚠️ Vui lòng chọn một trong các mô hình có sẵn bằng cách sử dụng lệnh /select"
        )
        return

    # Lưu lựa chọn của người dùng
    user_model_choices[user_id] = model_choice
    await update.message.reply_text(
        f"✅ Bạn đã chọn {model_choice}.\n"
        "🖼 Bây giờ hãy gửi ảnh bệnh lúa của bạn bằng lệnh /upload"
        "\nℹ️ Nếu muốn điều chỉnh độ tin cậy, hãy sử dụng lệnh /conf"
    )

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📤 Vui lòng gửi ảnh bệnh lúa của bạn.\n"
        "ℹ️ Lưu ý: Chỉ chấp nhận file ảnh (JPG, PNG)"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Kiểm tra xem người dùng đã chọn mô hình chưa
    if user_id not in user_model_choices:
        await update.message.reply_text(
            "⚠️ Vui lòng chọn mô hình dự đoán trước bằng lệnh /select"
        )
        return

    try:
        # Lấy ảnh với chất lượng cao nhất
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        # Tải ảnh về
        photo_data = await file.download_as_bytearray()
        
        conf_value = user_confidence_settings.get(user_id, 0.4)
        files = {'file': ('image.jpg', photo_data, 'image/jpeg')}
        params = {
            'model_type': user_model_choices[user_id],
            'conf': conf_value
        }

        await update.message.reply_text("🔄 Đang xử lý ảnh...")
        
        response = requests.post(API_URL, params=params, files=files)
        
        if response.status_code == 200:
            result = response.json()
            await update.message.reply_text(
                f"✅ Kết quả phân tích:\n\n"
                f"🔍 Mô hình: {result['model']}\n"
                f"🌾 Bệnh: {result['disease']}\n"
                f"📊 Độ tin cậy: {result['confidence']*100:.2f}%"
            )
            if 'image' in result:
                img_data = base64.b64decode(result['image'])
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=BytesIO(img_data),
                    caption="🖼️ Ảnh đã phân tích với vùng bệnh được đánh dấu"
                )
                # Giải phóng bộ nhớ
                del img_data
        else:
            await update.message.reply_text(
                "❌ Có lỗi xảy ra khi phân tích ảnh. Vui lòng thử lại sau."
            )
        # Giải phóng bộ nhớ
        del photo_data, files, response
    except Exception as e:
        print(f"Error: {str(e)}")
        await update.message.reply_text(
            "❌ Không thể kết nối đến server. Vui lòng thử lại sau."
        )
    finally:
        # Đảm bảo giải phóng bộ nhớ trong mọi trường hợp
        try:
            del photo, file
        except:
            pass
def main():
    app = ApplicationBuilder().token(TOKEN_TELE).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("select", select))
    app.add_handler(CommandHandler("conf", set_confidence))
    app.add_handler(CommandHandler("upload", upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_model_choice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()