import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

# Подменяем KafkaProducer, чтобы Producer.__init__ не выкидывал ошибку NoBrokersAvailable
with patch("producer.KafkaProducer", return_value=MagicMock()):
    from api import app  # импортируем приложение уже с патчем

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"health_check": "OK"}

@patch("api.Producer.send")
def test_predict(mock_send):
    payload = {
        "Doors": 4,
        "Year": 2020,
        "Owner_Count": 1,
        "Brand": "Toyota",
        "Model": "Corolla",
        "Fuel_Type": "Petrol",
        "Transmission": "Manual",
        "Engine_Size": 1.8,
        "Mileage": 15000
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data