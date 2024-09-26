import queue
import asyncio
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from logger import setup_logging

logger = setup_logging()

# Kafka 프로듀서 및 컨슈머 전역 변수
producer = None # pylint: disable=invalid-name
consumer = None # pylint: disable=invalid-name
message_queue = queue.Queue()

# Kafka 프로듀서 설정
producer = Producer({'bootstrap.servers': 'kafka-service:9092'})

# Kafka 메시지 배달 리포트 콜백 함수
def delivery_report(err, msg):
    if err:
        logger.error("Message delivery failed: %s % err")
    else:
        logger.info("Message delivered to %s [%s]", {msg.topic()}, {msg.partition()})

# Kafka로 질문을 전송하는 함수
def send_question_to_kafka(user_message, user_id):
    producer.produce('query-business', key=str(user_id), value=user_message, callback=delivery_report)
    producer.flush()

# Kafka 메시지를 소비하는 함수
def start_kafka_consumer():
    global consumer  # pylint: disable=global-statement

    consumer = Consumer({
        'bootstrap.servers': 'kafka-service:9092',
        'group.id': 'ollama-service-group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['query-business-response'])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: # pylint: disable=protected-access
                    continue
                raise KafkaException(msg.error())

            response_key = msg.key().decode('utf-8')
            response_value = msg.value().decode('utf-8')

            if message_queue.empty():
                continue

            message, user_id = message_queue.get()

            if user_id == response_key:
                logger.info("Response for user %s: %s", user_id, response_value)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(message.edit_text(f"Response: {response_value}"))
                loop.close()

    except KafkaException as e:  # 특정 예외만 잡도록 수정
        logger.error("KafkaException in Kafka consumer: %s", e)

# Kafka Consumer 종료 함수
def shutdown_consumer():
    if consumer:
        consumer.close()
        logger.info("Kafka consumer closed.")
