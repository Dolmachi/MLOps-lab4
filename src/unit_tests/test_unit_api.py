import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

# Патчим метод get_database, чтобы он возвращал объект-заглушку
# с нужной коллекцией predictions
with patch("database.MongoDBConnector.get_database", return_value=MagicMock(
    predictions=MagicMock(insert_one=lambda x: type("Obj", (object,), {"inserted_id": "12345"})())
)):
    from api import app  # Импортируем после патчинга

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"health_check": "OK"}

def test_predict():
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