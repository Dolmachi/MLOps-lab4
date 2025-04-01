import os
import sys
import yaml
from pymongo import MongoClient
from confluent_kafka import Consumer, KafkaError
from logger import Logger
import json

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

SHOW_LOG = True
logger = Logger(SHOW_LOG).get_logger(__name__)

# Загружаем настройки из secrets.yml
base_dir = os.path.dirname(__file__)
secrets_file_path = os.path.join(base_dir, '..', 'secrets.yml')
with open(secrets_file_path, "r") as file:
    secrets = yaml.safe_load(file)

# Настройки для Kafka Consumer
kafka_config = {
    'bootstrap.servers': secrets['kafka']['bootstrap_servers'],
    'group.id': 'mongo_consumer_group',
    'auto.offset.reset': 'earliest'
}
kafka_topic = secrets['kafka']['topic']

# Настройки для MongoDB
try:
    host = secrets['host']
    port = secrets['port']
    user = secrets['user']
    password = secrets['password']
    dbname = secrets['name']
except KeyError as e:
    logger.error(f"Отсутствует ключ авторизации: {e}")
    sys.exit(1)

# Формируем URI для MongoDB
uri = f"mongodb://{user}:{password}@{host}:{port}/{dbname}?authSource=admin"
logger.info(f"MongoDB URI: {uri}")

# Подключаемся к MongoDB
try:
    client = MongoClient(uri)
    # Проверка подключения
    client.admin.command('ping')
    logger.info(f"Успешное подключение к базе данных '{dbname}' на {host}:{port}")
except Exception as e:
    logger.error("Ошибка подключения к MongoDB", exc_info=True)
    sys.exit(1)

db = client[dbname]

# Инициализируем Kafka Consumer
consumer = Consumer(kafka_config)
consumer.subscribe([kafka_topic])

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
    client.close()
    logger.info("Kafka Consumer и MongoDB клиент закрыты")