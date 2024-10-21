import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from kafka_service import send_question_to_kafka
from kafka_service import user_message_ids
from kafka_service import message_cache
from logger import setup_logging

logger = setup_logging()
# Telegram 명령어 처리 함수
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your assistant.")

# Kafka로 질문 전송하는 함수
async def send_question_to_ollama_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = str(update.message.from_user.id)
    message = await update.message.reply_text("Processing...")

    #message_cache[message.message_id] = message
    message_cache[user_id] = message
    # 메시지 ID 저장
    user_message_ids[user_id] = message.message_id

    # Kafka로 메시지 전송
    send_question_to_kafka(user_message, user_id)

# Telegram 애플리케이션 생성 함수
def create_telegram_application():
    load_dotenv(verbose=True)
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") # pylint: disable=invalid-name

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # 명령어 및 메시지 핸들러 등록
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_question_to_ollama_service))

    return application
