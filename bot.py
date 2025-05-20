from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

# 관리자 ID 리스트
ADMIN_IDS = [8051010893, 8027469689, 7714652071]
# 인증 코드
AUTH_CODE = "888"
# 사용자 저장 파일명
USER_FILE = "users.json"

# 등록된 사용자 로드 함수
def load_registered_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# 등록된 사용자 저장 함수
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

    # 인증 코드 입력 시 사용자 등록
    if text == AUTH_CODE:
        if user_id not in registered_users:
            registered_users.add(user_id)
            save_registered_users(registered_users)
        await update.message.reply_text("✅ 사용자 등록완료")
        return

    # 관리자가 ##로 시작하는 메시지 입력 시 모든 등록자에게 공지 전송
    if text.startswith("##"):
        if user_id in ADMIN_IDS:
            content = text.replace("##", "").strip()
            await broadcast_to_users(context, content)
        else:
            await update.message.reply_text("❌ 이 기능은 관리자만 사용할 수 있습니다.")
        return

    # 등록되지 않은 사용자는 무시 (단 관리자 제외)
    if user_id not in registered_users and user_id not in ADMIN_IDS:
        return

# 공지 전송 함수
async def broadcast_to_users(context: ContextTypes.DEFAULT_TYPE, message: str):
    for user_id in registered_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            print(f"✅ 공지 전송 성공: {user_id}")
        except Exception as e:
            print(f"⚠️ 전송 실패 - 사용자 {user_id}: {e}")

if __name__ == "__main__":
    TOKEN = "8029823254:AAEEhAbrAZGlCOFJrJtKEhcKcTi8elvIRps"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("✅ 로봇 실행 중...")
    app.run_polling()


