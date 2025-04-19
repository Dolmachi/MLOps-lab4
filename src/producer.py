import json
from kafka import KafkaProducer
from logger import Logger

class Producer:
    def __init__(self):
        self.logger = Logger(True).get_logger(__name__)
        self.producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        
    def send(self, payload: dict):
        """Отправить результат предикта в топик 'predictions'."""
        try:
            self.producer.send("predictions", payload)
            self.logger.info("Sent message to Kafka topic 'predictions'")
        except Exception as e:
            self.logger.error("Error sending to Kafka", exc_info=True)