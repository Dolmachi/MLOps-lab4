from predict import PipelinePredictor
from pydantic import BaseModel
from producer import Producer
from fastapi import FastAPI
from logger import Logger
import pandas as pd

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
        self.producer = Producer()
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
            
            # Подготовка данных для сохранения в Kafka
            result = {
                "input": features.model_dump(),
                "prediction": prediction
            }
            
            # Отправляем результат в топик kafka 'predictions'
            self.producer.send(result)
                
            return {"prediction": prediction}

    def get_app(self):
        """Возвращает экземпляр FastAPI приложения"""
        return self.app


# Создаем экземпляр API
api = CarPriceAPI()
app = api.get_app()