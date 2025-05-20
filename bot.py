import json
import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# ✅ 관리자 ID (여러 명 지원)
ADMIN_IDS = [8051010893, 8027469689, 7714652071]  # 실제 관리자 Telegram user_id

# ✅ 사용자 등록 코드
AUTH_CODE = "888"

# ✅ 사용자 저장 파일
USER_FILE = "users.json"

# ✅ 사용자 로딩
def load_registered_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# ✅ 사용자 저장
def save_registered_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f)

# ✅ 등록자 메모리 로딩
registered_users = load_registered_users()

# /start 핸들러
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❗️알림봇을 설정하시려면 코드를 입력해주세요")

# ✅ 일반 메시지 핸들러
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return

    text = update.message.text.strip()
    user_id = update.effective_user.id

    # 사용자 등록
    if text == AUTH_CODE:
        if user_id not in registered_users:
            registered_users.add(user_id)
            save_registered_users(registered_users)
        await update.message.reply_text("✅ 사용자 등록완료")
        return

    # 관리자 공지
    if text.startswith("##"):
        if user_id in ADMIN_IDS:
            content = text.replace("##", "").strip()
            await broadcast_to_users(context, content)
        else:
            await update.message.reply_text("❌ 이 기능은 관리자만 사용할 수 있습니다.")
        return

    # 등록되지 않은 사용자 → 반응 없음
    if user_id not in registered_users and user_id not in ADMIN_IDS:
        return

# ✅ 브로드캐스트 함수
async def broadcast_to_users(context: ContextTypes.DEFAULT_TYPE, message: str):
    for user_id in registered_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            print(f"✅ 공지 전송 성공: {user_id}")
        except Exception as e:
            print(f"⚠️ 전송 실패 - 사용자 {user_id}: {e}")

# ✅ 비동기 메인 실행 함수
async def main():
    bot_token = "7596584111:AAFR2XNBybeYmmVMz3dwlxmpje9uBCMJ4w4"  # ← BotFather에서 받은 토큰
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # ✅ 웹훅 비활성화 (중복 충돌 방지)
    await app.bot.delete_webhook()

    print("✅ 봇 실행 중...")
    await app.run_polling()

# ✅ 엔트리 포인트
if __name__ == "__main__":
    asyncio.run(main())
