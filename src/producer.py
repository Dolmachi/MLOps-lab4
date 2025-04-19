import json
from kafka import KafkaProducer
from logger import Logger

logger = Logger(True).get_logger(__name__)

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_prediction(payload: dict):
    """Отправить результат предикта в топик 'predictions'."""
    try:
        producer.send("predictions", payload)
        producer.flush()
        logger.info("Sent message to Kafka topic 'predictions'")
    except Exception as e:
        logger.error("Error sending to Kafka", exc_info=True)