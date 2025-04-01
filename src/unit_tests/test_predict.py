import pytest
import os
import pandas as pd
from unittest.mock import patch
import sys

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from predict import PipelinePredictor

@pytest.fixture
def predictor():
    """Создаёт объект предиктора перед каждым тестом"""
    return PipelinePredictor()

def test_init(predictor):
    """Тестируем __init__(): пайплайн должен загружаться корректно"""
    assert predictor.pipeline is not None, "Пайплайн не был загружен"
    assert hasattr(predictor.pipeline, "predict"), "Пайплайн не имеет метода predict"

def test_predict(predictor):
    """Тестируем predict(): должна выдавать предсказание"""
    dummy_input = pd.DataFrame({
        "Doors": [4], "Year": [2019], "Owner_Count": [1],
        "Brand": ["BMW"], "Model": ["X5"], "Fuel_Type": ["Diesel"],
        "Transmission": ["Automatic"], "Engine_Size": [3.0], "Mileage": [45000]
    })
    
    prediction = predictor.predict(dummy_input)
    
    assert isinstance(prediction[0], float), "Выход предсказания должен быть float"

def test_test(predictor):
    """Тестируем test(): должен выполняться без ошибок"""
    with patch("sys.argv", ["predict.py", "--test", "smoke"]):
        assert predictor.test() == True, "Smoke test не прошёл"
    with patch("sys.argv", ["predict.py", "--test", "func"]):
        assert predictor.test() == True, "Smoke test не прошёл"