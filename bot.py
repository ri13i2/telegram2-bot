from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
import json
import os

# 관리자 ID 및 인증 코드 설정
ADMIN_IDS = [8051010893, 8027469689, 7714652071]
AUTH_CODE = "888"
USER_FILE = "users.json"

# 사용자 정보 불러오기 및 저장
def load_registered_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_registered_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f)

registered_users = load_registered_users()

# /start 명령어 처리
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❗️알림봇을 설정하시려면 코드를 입력해주세요")

# 일반 메시지 처리
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

# 사용자에게 메시지 전송
async def broadcast_to_users(context: ContextTypes.DEFAULT_TYPE, message: str):
    for user_id in registered_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            print(f"✅ 공지 전송 성공: {user_id}")
        except Exception as e:
            print(f"⚠️ 전송 실패 - 사용자 {user_id}: {e}")

# 메인 실행
def main():
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # ← 실제 토큰으로 바꾸세요
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ 로봇 실행 중...")
    app.run_polling()

if __name__ == "__main__":
    main()

