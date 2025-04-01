from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from predict import PipelinePredictor
from database import get_database
from logger import Logger


SHOW_LOG = True
logger = Logger(SHOW_LOG).get_logger(__name__)

predictor = PipelinePredictor()

db = get_database()

app = FastAPI()

# Определяем модель входных данных
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
    
    # Подготовка данных для сохранения в MongoDB
    result_data = {
         "input": features.model_dump(),
         "prediction": prediction[0],
         "timestamp": datetime.utcnow().isoformat()
    }
    
    # Сохраняем результат в коллекцию 'predictions'
    try:
        result = db.predictions.insert_one(result_data)
        logger.info(f"Prediction saved with id: {result.inserted_id}")
    except Exception as e:
        logger.error("Error saving prediction", exc_info=True)
    
    return {"prediction": prediction[0]}

