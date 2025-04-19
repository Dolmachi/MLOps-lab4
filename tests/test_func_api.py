import os
import sys
import json
import time
import requests
import configparser
from pymongo import MongoClient
from sklearn.metrics import r2_score

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from logger import Logger

logger = Logger(True).get_logger(__name__)

config = configparser.ConfigParser()
config_path = os.path.join(os.getcwd(), "config_secret.ini")
config.read(config_path)
db_config = config["DATABASE"]

host = db_config.get("host")
port = db_config.get("port")
user = db_config.get("user")
password = db_config.get("password")
DB_NAME = db_config.get("name")

MONGO_URL = f"mongodb://{user}:{password}@{host}:{port}/"

# URL API, запущенного в контейнере
SERVER_URL = "http://localhost:8000/predict"

# Путь до папки с тестовыми JSON-файлами
TESTS_DIR = os.path.join(os.path.dirname(__file__), "test_data")

def test_func_api_r2():
    """
    Функциональный тест API:
    - Для каждого тестового JSON отправляем запрос к API.
    - Из базы извлекаем записанные предсказания.
    - Вычисляем R² между предсказаниями из базы и истинными значениями.
    - Тест проходит, если R² >= 0.8.
    """
    test_files = [os.path.join(TESTS_DIR, f) for f in os.listdir(TESTS_DIR) if f.endswith(".json")]
    
    expected_values = []
    # Отправляем запросы к API
    for test_file in test_files:
        with open(test_file, "r") as f:
            data = json.load(f)
        input_data = data["X"]
        expected = data["y"]["prediction"]
        expected_values.append(expected)
        
        response = requests.post(SERVER_URL, json=input_data)
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
        # Короткая задержка, чтобы запись успела произойти в базе
        time.sleep(0.5)
    
    # Подключаемся к базе данных и собираем предсказания
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    db_predictions = []
    
    for test_file in test_files:
        with open(test_file, "r") as f:
            data = json.load(f)
        input_data = data["X"]
        record = db.predictions.find_one({"input": input_data})
        assert record is not None, f"Record for input {input_data} not found in database"
        db_predictions.append(record.get("prediction"))
    
    # Вычисляем R^2-метрику
    r2 = r2_score(expected_values, db_predictions)
    assert r2 >= 0.8, f"R^2 Score {r2:.4f} is below acceptable threshold"
    logger.info(f"Functional test was successful! R^2 Score: {r2:.4f}")