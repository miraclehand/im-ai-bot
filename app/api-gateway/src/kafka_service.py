import asyncio
import uuid
import json
from datetime import datetime
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from logger import setup_logging

logger = setup_logging()

# Kafka 프로듀서 및 컨슈머 전역 변수
producer = None # pylint: disable=invalid-name
consumer = None # pylint: disable=invalid-name

bot = None # pylint: disable=invalid-name

user_message_ids = {} # 사용자별 메시지 ID를 저장할 딕셔너리
message_cache = {}

# Kafka 프로듀서 설정
producer = Producer({'bootstrap.servers': 'kafka.default.svc.cluster.local:9092'})

# Kafka 메시지 배달 리포트 콜백 함수
def delivery_report(err, msg):
    if err:
        logger.error("Message delivery failed: %s % err")
    else:
        logger.info("Message delivered to %s [%s]", {msg.topic()}, {msg.partition()})

# Kafka로 질문을 전송하는 함수
def send_question_to_kafka(user_message, user_id):
    data = {
        "question_id": str(uuid.uuid4()),  # 고유한 질문 ID 생성
        "user_id": str(user_id),
        "message": user_message,
        "timestamp": datetime.now().isoformat()
    }
    producer.produce('query-business', key=str(user_id), value=json.dumps(data), callback=delivery_report)
    producer.flush()
    logger.info("send kafka %s", data)

# 응답을 텔레그램으로 보내는 비동기 함수
async def update_telegram_response(chat_id, message_id, response):
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=response)

async def abcde(user_id, message_id, response_value):
    # Instead of fetching the message, we assume you know the original text
    if user_id in user_message_ids:
        # Assuming you stored the original text in user_message_ids[user_id]
        current_text = user_message_ids[user_id]

        updated_text = (str(current_text) + " " + str(response_value)).strip()
        await update_telegram_response(user_id, message_id, updated_text)

# Kafka 메시지를 소비하는 함수
def start_kafka_consumer(telegram_bot):
    global consumer  # pylint: disable=global-statement
    global bot  # pylint: disable=global-statement

    bot = telegram_bot

    consumer = Consumer({
        'bootstrap.servers': 'kafka.default.svc.cluster.local:9092',
        'group.id': 'ollama-service-group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['query-business-response'])
    #logger.info("message_queue in kafka %s %s", message_queue, str(message_queue.empty()))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    updated_text = ''
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            #logger.info("Consume, msg, %s %s", msg, str(message_queue.empty()))
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: # pylint: disable=protected-access
                    continue
                raise KafkaException(msg.error())

            user_id = msg.key().decode('utf-8')
            response_value = msg.value().decode('utf-8')
            #{"chunk": "d", chunk_id":12, "is_final": false}
            res = json.loads(response_value)
            chunk = res['chunk'].strip()
            is_final = res['is_final']

            logger.info("Receieved response %s %s", user_id, chunk)

            """
            if user_id in user_message_ids:
                message_id = user_message_ids[user_id]
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(abcde(user_id, message_id, response_value))
            """
            if not chunk:
                continue
            if user_id in message_cache:
                cached_message = message_cache[user_id]
                updated_text = updated_text + chunk
                #loop.run_until_complete(update_message.edit_text(updated_text))
                loop.run_until_complete(cached_message.edit_text(updated_text))
                #loop.run_until_complete(update_message.reply_text(response_value))
            if is_final:
                updated_text = ''
            """
            if user_id in user_message_ids:
                message_id = user_message_ids[user_id]
                logger.info("user_id: %s, message_id: %s", str(user_id), str(message_id))
                #current_text = await bot.get_chat(user_id).message(message_id).text
                #current_text = await bot.get_messages(user_id, message_id)

                logger.info("bot: %s", str(dir(bot.get_chat(user_id))))
                #current_text = loop.run_until_complete(bot.get_messages(user_id, message_id))
                current_text = loop.run_until_complete(bot.get_chat(user_id).messages(message_id).text)
                updated_text = (current_text + " " + response_value).strip()
                loop.run_until_complete(update_telegram_response(user_id, message_id, updated_text))
            """


            """
            if response_key not in user_message:
                continue

            logger.info("message_queue in nested kafka %s %s", message_queue, str(message_queue.empty()))
            if message_queue.empty():
                continue

            message, user_id = message_queue.get()
            user_message[user_id] = message


            logger.info("Consume, user_id %s: %s", user_id, response_key)
            if user_id == response_key:
                logger.info("Response for user %s: %s", user_id, response_value)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(message.edit_text(f"Response: {response_value}"))
                loop.close()
            """

    except KafkaException as e:  # 특정 예외만 잡도록 수정
        logger.error("KafkaException in Kafka consumer: %s", e)
    finally:
        loop.close()


# Kafka Consumer 종료 함수
def shutdown_consumer():
    if consumer:
        consumer.close()
        logger.info("Kafka consumer closed.")
