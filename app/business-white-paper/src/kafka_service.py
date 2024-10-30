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

            value = redis.get(question)
            if value:
                logger.info("redis question:%s, value:%s", question, value)
                response = {
                    'chunk': value,
                    'chunk_id': 1,
                    'is_final': True
                }
                producer.produce(
                    'query-business-response',
                    key=key,
                    value=json.dumps(response).encode('utf-8')
                )
                producer.flush()
                continue
            response_value = ""
            chunk_count = 0
            for chunk in generate_answer(question):
                chunk_count += 1
                response = {
                    'chunk': chunk,
                    'chunk_id': chunk_count,
                    'is_final': False
                }
                producer.produce(
                    'query-business-response',
                    key=key,
                    value=json.dumps(response).encode('utf-8')
                )
                producer.flush()
                response_value += chunk
                #logger.info("Sent chunk %d for key=%s: %s", chunk_count, key, chunk)
            final_response = {
                'chunk': '',
                'chunk_id': chunk_count + 1,
                'is_final': True
            }
            producer.produce(
                'query-business-response',
                key=key,
                value=json.dumps(final_response).encode('utf-8')
            )
            producer.flush()
            logger.info("Completed generation for key=%s response_value:%s", key, response_value)
            redis.set(question, response_value)

            """
            answer = "".join(generate_answer(question))

            logger.info("Generated answer for key=%s: %s (Question: %s)", key, answer, question)

            producer.produce('query-business-response', key=key, value=answer.encode('utf-8'))
            producer.flush()
            """

    except KafkaException as e:
        logger.error("KafkaException in Kafka consumer: %s", e)

def shutdown_consumer():
    if consumer:
        consumer.close()
        logger.info("Kafka consumer closed.")
