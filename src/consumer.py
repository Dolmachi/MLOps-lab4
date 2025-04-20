import json
from kafka import KafkaConsumer
from database import MongoDBConnector
from logger import Logger

class Consumer:
    def __init__(self):
        self.logger = Logger(True).get_logger(__name__)
        self.db = MongoDBConnector().get_database()
        self.consumer = KafkaConsumer(
            "predictions",
            bootstrap_servers="kafka:9092",
            group_id="prediction-group",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )

    def run(self):
        for msg in self.consumer:
            try:
                self.db.predictions.insert_one(msg.value)
                self.logger.info(f"Saved to MongoDB: {msg.value}")
            except Exception: # pragma: no cover
                self.logger.error("Error writing to MongoDB", exc_info=True)


if __name__ == "__main__": # pragma: no cover
    consumer = Consumer()
    consumer.run()