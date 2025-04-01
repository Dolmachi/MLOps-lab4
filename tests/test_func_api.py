import pytest
import json
import math
import requests
import os
import sys
from pymongo import MongoClient
from sklearn.metrics import r2_score
from time import sleep

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from logger import Logger
from database import get_database


# Пути и URL
BASE_DIR = os.path.dirname(__file__)
TESTS_DIR = os.path.join(BASE_DIR, "test_data")
SERVER_URL = "http://localhost:8000/predict"
SHOW_LOG = True

logger = Logger(True).get_logger(__name__)

def test_functional_predict_db():
    """Тест: API возвращает корректное предсказание и сохраняет его в базе данных."""
    # Загружаем тестовые данные
    test_files = [os.path.join(TESTS_DIR, f) for f in os.listdir(TESTS_DIR) if f.endswith('.json')]
    
    all_inputs = []
    all_expected = []
    
    for test_file in test_files:
        with open(test_file, "r") as f:
            data = json.load(f)
        all_inputs.append(data["X"])
        all_expected.append(data["y"]["prediction"])
    
    predictions = []
    for input_data in all_inputs:
        response = requests.post(SERVER_URL, json=input_data)
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
        result = response.json()
        assert "prediction" in result, "No prediction in response"
        predictions.append(result["prediction"])
    
    # Проверка R² для всех примеров
    for pred, exp in zip(predictions, all_expected):
        assert math.isclose(pred, exp, rel_tol=0.01), f"Expected {exp}, got {pred}"
        
    r2 = r2_score(all_expected, predictions)
    logger.info(f"Overall R2 Score: {r2:.4f}")
    
    # Даем немного времени на то, чтобы API записало данные в базу
    sleep(3)
    
    db = get_database()
    
    # Проверяем, что в базе данных появился документ с предсказанием
    docs = list(db.predictions.find())
    assert len(docs) >= len(test_files), "Не все предсказания были сохранены в БД"

    for expected in all_expected:
        # Ищем документ, в котором поле prediction близко к ожидаемому
        match = any(math.isclose(doc.get("prediction", 0), expected, rel_tol=0.01) for doc in docs)
        assert match, f"Предсказание {expected} не найдено в БД"
    
    logger.info("Функциональный тест с проверкой базы данных пройден успешно.")
