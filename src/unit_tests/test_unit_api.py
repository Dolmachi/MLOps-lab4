import pytest
import json
import math
import sys
import os
import mongomock
import pymongo
from fastapi.testclient import TestClient

# Задаём подмену до импорта других модулей
pymongo.MongoClient = mongomock.MongoClient

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from api import app  # Импортируем API

client = TestClient(app)  # Создаём тестового клиента

# Получаем пути до тестовых json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)) ) 
TESTS_DIR = os.path.join(BASE_DIR, "tests", "test_data")

@pytest.mark.parametrize("test_file", [
    os.path.join(TESTS_DIR, "test_0.json"),
    os.path.join(TESTS_DIR, "test_1.json")
])
def test_unit_api(test_file):
    """Unit тестирование имитационного API"""
    # Открываем тест
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    # Отправляем POST-запрос в API
    response = client.post("/predict", json=test_data["X"])
    
    # Проверяем, что API вернул 200 OK
    assert response.status_code == 200

    # Проверяем, что в ответе есть предсказание
    assert "prediction" in response.json()

    # Ожидаемое и полученное предсказание
    y_true = test_data["y"]["prediction"]
    y_pred = response.json()["prediction"]

    # Проверяем, что предсказание близко к ожидаемому (допуск ±1%)
    assert math.isclose(y_pred, y_true, rel_tol=0.01)
