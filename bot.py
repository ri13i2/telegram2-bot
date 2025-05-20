from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

ADMIN_IDS = [8051010893, 8027469689, 7714652071]
AUTH_CODE = "888"
USER_FILE = "users.json"

def load_registered_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_registered_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f)

registered_users = load_registered_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❗️알림봇을 설정하시려면 코드를 입력해주세요")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return

    text = update.message.text.strip()
    user_id = update.effective_user.id

    if text == AUTH_CODE:
        if user_id not in registered_users:
            registered_users.add(user_id)
            save_registered_users(registered_users)
        await update.message.reply_text("✅ 사용자 등록완료")
        return

    if text.startswith("##"):
        if user_id in ADMIN_IDS:
            content = text.replace("##", "").strip()
            await broadcast_to_users(context, content)
        else:
            await update.message.reply_text("❌ 이 기능은 관리자만 사용할 수 있습니다.")
        return

    if user_id not in registered_users and user_id not in ADMIN_IDS:
        return

async def broadcast_to_users(context: ContextTypes.DEFAULT_TYPE, message: str):
    for user_id in registered_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            print(f"✅ 공지 전송 성공: {user_id}")
        except Exception as e:
            print(f"⚠️ 전송 실패 - 사용자 {user_id}: {e}")

if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # 환경변수로 토큰 설정 권장
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN 환경변수가 설정되지 않았습니다.")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("✅ 로봇 실행 중...")
    app.run_polling()


