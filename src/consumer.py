import os
import sys
import yaml
from confluent_kafka import Consumer, KafkaError
from logger import Logger
from database import get_database  # Добавляем для подключения к MongoDB

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

SHOW_LOG = True
logger = Logger(SHOW_LOG).get_logger(__name__)

# Загружаем настройки Kafka из secrets.yml
base_dir = os.path.dirname(__file__)
secrets_file_path = os.path.join(base_dir, '..', 'secrets.yml')
with open(secrets_file_path, "r") as file:
    secrets = yaml.safe_load(file)

# Настройки для Kafka Consumer
kafka_config = {
    'bootstrap.servers': secrets['kafka']['bootstrap_servers'],
    'group.id': 'car_price_consumer_group',
    'auto.offset.reset': 'earliest'
}
kafka_topic = secrets['kafka']['topic']

# Инициализируем Kafka Consumer
consumer = Consumer(kafka_config)
consumer.subscribe([kafka_topic])

# Подключаемся к MongoDB
db = get_database()

logger.info(f"Запускаем Kafka Consumer для топика: {kafka_topic}")

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logger.info("Достигнут конец раздела топика")
            else:
                logger.error(f"Ошибка Kafka: {msg.error()}")
            continue

        # Обрабатываем полученное сообщение
        key = msg.key().decode('utf-8') if msg.key() else None
        value = msg.value().decode('utf-8')
        logger.info(f"Получено сообщение - Ключ: {key}, Значение: {value}")

        # Сохраняем сообщение в MongoDB
        try:
            import json
            data = json.loads(value)  # Преобразуем JSON-строку в словарь
            data['kafka_message_id'] = key  # Добавляем ID сообщения
            result = db.predictions.insert_one(data)
            logger.info(f"Сообщение сохранено в MongoDB с id: {result.inserted_id}")
        except Exception as e:
            logger.error("Ошибка сохранения в MongoDB", exc_info=True)

except KeyboardInterrupt:
    logger.info("Consumer прерван пользователем")
finally:
    consumer.close()
    logger.info("Kafka Consumer закрыт")