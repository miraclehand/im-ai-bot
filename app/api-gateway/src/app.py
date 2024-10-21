import atexit
import threading
from telegram_bot import create_telegram_application
from kafka_service import shutdown_consumer
from kafka_service import start_kafka_consumer
from logger import setup_logging

# 로그 설정
logger = setup_logging()

if __name__ == '__main__':
    # 종료 시 Kafka Consumer 종료 함수 등록
    atexit.register(shutdown_consumer)

    # Telegram 봇 실행
    application = create_telegram_application()

    # Kafka 메시지 소비 스레드 시작
    threading.Thread(target=start_kafka_consumer, args=(application.bot,)).start()
    application.run_polling()
