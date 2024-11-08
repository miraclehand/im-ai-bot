import json
from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
from llm_service import generate_answer
from logger import setup_logging
from redis_service import connect_to_redis_server

logger = setup_logging()

consumer_config = {
    'bootstrap.servers': 'kafka.default.svc.cluster.local:9092',
    'group.id': 'ollama-service-group',
    'auto.offset.reset': 'earliest'
}

producer_config = {
    'bootstrap.servers': 'kafka.default.svc.cluster.local:9092'
}

consumer = Consumer(consumer_config)
producer = Producer(producer_config)

consumer.subscribe(['query-business'])

def consume_and_answer():
    logger.info('Starting consume_and_answer thread...')
    redis = connect_to_redis_server()

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: # pylint: disable=protected-access
                    continue
                raise KafkaException(msg.error())

            key = msg.key().decode('utf-8')
            json_string = msg.value().decode('utf-8')
            logger.info("json_string:%s", json_string)

            json_acceptable_string = json_string.replace("'", "\"")
            d = json.loads(json_acceptable_string)
            question = d.get('message')
            logger.info("question:%s", question)

            response_value = redis.get(question)
            if response_value:
                logger.info("=> redis question:%s, response_value:%s", question, response_value)
                response = create_response(response_value, 1, True)

                send_response(key, response)
                send_final_response(key, question, response_value)
                continue

            response_value = generate_answer(question)
            response = create_response(response_value, 1, True)

            send_response(key, response)
            send_final_response(key, question, response_value)

            redis.set(question, response_value)
    except KafkaException as e:
        logger.error("KafkaException in Kafka consumer: %s", e)

def create_response(chunk, chunk_id, is_final):
    return {
        'chunk': chunk,
        'chunk_id': chunk_id,
        'is_final': is_final
    }

def send_response(key, response):
    producer.produce(
        'query-business-response',
        key=key,
        value=json.dumps(response).encode('utf-8')
    )
    producer.flush()

def send_final_response(key, question, response_value):
    response = {
        "qa": {
            'question': question,
            'answer': response_value,
        }
    }
    logger.info("send_final_response. query-business-qa key:%s, %s", key, response)
    producer.produce('query-business-qa', key=key, value=json.dumps(response).encode('utf-8'))
    producer.flush()

def shutdown_consumer():
    if consumer:
        consumer.close()
        logger.info("Kafka consumer closed.")
