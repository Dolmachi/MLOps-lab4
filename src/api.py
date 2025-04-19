from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
import sys

from predict import PipelinePredictor
from database import MongoDBConnector
from logger import Logger

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

class CarPriceAPI:
    def __init__(self):
        """Инициализация API и зависимостей"""
        self.logger = Logger(True).get_logger(__name__)
        self.app = FastAPI()
        self.predictor = PipelinePredictor()
        self.db = MongoDBConnector().get_database()
        self._register_routes()

    def _register_routes(self):
        """Регистрация маршрутов API"""
        @self.app.get('/')
        def health_check():
            return {'health_check': 'OK'}

        @self.app.post("/predict")
        def predict(features: CarFeatures):
            # Получаем данные и делаем предсказание
            input_data = pd.DataFrame([features.model_dump()])
            prediction = self.predictor.predict(input_data)[0]
            
            # Подготовка данных для сохранения в MongoDB
            result_data = {
                "input": features.model_dump(),
                "prediction": prediction
            }
            
            # Сохраняем результат в коллекцию 'predictions'
            try:
                result = self.db.predictions.insert_one(result_data)
                self.logger.info(f"Prediction saved with id: {result.inserted_id}")
            except Exception as e: # pragma: no cover
                self.logger.error("Error saving prediction", exc_info=True)
                
            return {"prediction": prediction}

    def get_app(self):
        """Возвращает экземпляр FastAPI приложения"""
        return self.app


# Создаем экземпляр API
api = CarPriceAPI()
app = api.get_app()