import asyncio
import uuid
import json
from datetime import datetime
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from logger import setup_logging

logger = setup_logging()

producer = None # pylint: disable=invalid-name
consumer = None # pylint: disable=invalid-name
bot = None # pylint: disable=invalid-name
user_message_ids = {}
message_cache = {}

producer = Producer({'bootstrap.servers': 'kafka.default.svc.cluster.local:9092'})

def delivery_report(err, msg):
    if err:
        logger.error("Message delivery failed: %s", err)
    else:
        logger.info("Message delivered to %s [%s]", msg.topic(), msg.partition())

def send_question_to_kafka(user_message, user_id):
    data = {
        "question_id": str(uuid.uuid4()),
        "user_id": str(user_id),
        "message": user_message,
        "timestamp": datetime.now().isoformat()
    }
    producer.produce('query-business', key=str(user_id), value=json.dumps(data), callback=delivery_report)
    producer.flush()
    logger.info("send kafka %s", data)

async def update_telegram_response(chat_id, message_id, response):
    current_message = await bot.get_message(chat_id, message_id)  # 현재 메시지를 가져옵니다.
    if current_message.text != response:  # 새 텍스트가 기존 텍스트와 다른지 확인합니다.
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=response)

async def process_kafka_message(user_id, response_value, cached_message, updated_text):
    try:
        res = json.loads(response_value)
        chunk = res['chunk'].strip()
        is_final = res['is_final']

        if not chunk:
            return updated_text, is_final

        new_text = updated_text + chunk

        if cached_message:
            if new_text != updated_text:  # 텍스트가 변경된 경우에만 업데이트
                await cached_message.edit_text(new_text)

        return new_text, is_final
    except Exception as e:
        logger.error("Error processing Kafka message: %s", e)
        return updated_text, False

def start_kafka_consumer(telegram_bot):
    global consumer, bot
    bot = telegram_bot

    consumer = Consumer({
        'bootstrap.servers': 'kafka.default.svc.cluster.local:9092',
        'group.id': 'ollama-service-group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['query-business-response'])

    updated_text = ''

    async def message_handler():
        nonlocal updated_text
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: # pylint: disable=protected-access
                    continue
                raise KafkaException(msg.error())

            user_id = msg.key().decode('utf-8')
            response_value = msg.value().decode('utf-8')

            if user_id in message_cache:
                cached_message = message_cache[user_id]
                updated_text, is_final = await process_kafka_message(
                    user_id,
                    response_value,
                    cached_message,
                    updated_text
                )

                if is_final:
                    updated_text = ''

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(message_handler())
    except KafkaException as e:
        logger.error("KafkaException in Kafka consumer: %s", e)
    finally:
        loop.close()

def shutdown_consumer():
    if consumer:
        consumer.close()
        logger.info("Kafka consumer closed.")
