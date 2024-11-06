import atexit
import threading
import asyncio
from telegram_bot import create_telegram_application
from kafka_service import shutdown_consumer, start_kafka_consumer
from logger import setup_logging

# 로그 설정
logger = setup_logging()

def run_kafka_consumer(application):
    """
    Kafka Consumer를 실행하는 함수.
    """
    # Kafka 메시지 소비 스레드 시작
    kafka_thread = threading.Thread(target=start_kafka_consumer, args=(application.bot,))
    kafka_thread.start()

def run_telegram_bot():
    """
    Telegram 봇을 실행하는 함수.
    """
    application = create_telegram_application()

    # Kafka Consumer를 백그라운드에서 실행
    run_kafka_consumer(application)

    # 새로운 이벤트 루프를 설정
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Telegram 봇 폴링 시작
    loop.run_until_complete(application.run_polling())

if __name__ == '__main__':
    # 종료 시 Kafka Consumer 종료 함수 등록
    atexit.register(shutdown_consumer)

    # Telegram 봇을 메인 스레드에서 실행
    run_telegram_bot()

