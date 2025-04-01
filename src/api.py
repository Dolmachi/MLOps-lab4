from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
import sys
from datetime import datetime
from confluent_kafka import Producer
import json
import yaml
import uuid

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from predict import PipelinePredictor
from logger import Logger


SHOW_LOG = True
logger = Logger(SHOW_LOG).get_logger(__name__)

# Загружаем настройки Kafka из secrets.yml
base_dir = os.path.dirname(__file__)
secrets_file_path = os.path.join(base_dir, '..', 'secrets.yml')
with open(secrets_file_path, "r") as file:
    secrets = yaml.safe_load(file)

# Настройки для Kafka Producer
kafka_config = {
    'bootstrap.servers': secrets['kafka']['bootstrap_servers']
}
kafka_topic = secrets['kafka']['topic']

# Инициализируем Kafka Producer
producer = Producer(kafka_config)

def delivery_report(err, msg):
    """Функция обратного вызова для проверки доставки сообщения."""
    if err is not None:
        logger.error(f"Ошибка доставки сообщения: {err}")
    else:
        logger.info(f"Сообщение доставлено в {msg.topic()} [раздел {msg.partition()}]")

predictor = PipelinePredictor()
app = FastAPI()

class CarFeatures(BaseModel):
    Doors: int
    Year: int
    Owner_Count: int
    Brand: str
    Model: str
    Fuel_Type: str
    Transmission: str
    Engine_Size: float
    Mileage: float

@app.post("/predict")
def predict_api(features: CarFeatures):
    # Преобразуем входные данные в DataFrame для предсказания
    input_data = pd.DataFrame([features.model_dump()])
    prediction = predictor.predict(input_data)

    # Подготовка данных для отправки в Kafka
    result_data = {
        "input": features.model_dump(),
        "prediction": prediction[0],
        "timestamp": datetime.utcnow().isoformat()
    }

    # Генерируем уникальный ID для сообщения
    message_id = str(uuid.uuid4())

    # Отправляем результат в Kafka
    try:
        producer.produce(
            kafka_topic,
            key=message_id,
            value=json.dumps(result_data),
            callback=delivery_report
        )
        producer.flush()
        logger.info(f"Предсказание отправлено в топик Kafka: {kafka_topic}")
    except Exception as e:
        logger.error("Ошибка отправки сообщения в Kafka", exc_info=True)
        raise

    return {"prediction": prediction[0]}