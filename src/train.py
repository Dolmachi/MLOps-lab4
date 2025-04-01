import configparser
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler, OneHotEncoder
from sklearn.metrics import r2_score
import pickle
import sys
import traceback

from logger import Logger

SHOW_LOG = True


class ForestPipelineModel():
    def __init__(self) -> None:
        # Создаем объекты логера и конфигуратора,
        # и считываем конфигурацию
        logger = Logger(SHOW_LOG)
        self.config = configparser.ConfigParser()
        self.log = logger.get_logger(__name__)
        self.config.read("config.ini")
        
        # Загружаем данные
        try:
            self.X_train = pd.read_csv(self.config["SPLIT_DATA"]["X_train"], index_col=0)
            self.y_train = pd.read_csv(self.config["SPLIT_DATA"]["y_train"], index_col=0).values.ravel()
            self.X_test = pd.read_csv(self.config["SPLIT_DATA"]["X_test"], index_col=0)
            self.y_test = pd.read_csv(self.config["SPLIT_DATA"]["y_test"], index_col=0).values.ravel()
            self.log.info("Данные загружены успешно")
        except FileNotFoundError: # pragma: no cover
            self.log.error(traceback.format_exc())
            sys.exit(1)
        
        # Определение колонок для преобразования
        self.ordinal_columns = ["Doors", "Year", "Owner_Count"]
        self.categorical_columns = ["Brand", "Model", "Fuel_Type", "Transmission"]
        self.numeric_columns = ["Engine_Size", "Mileage"]

        # Путь для сохранения пайплайна
        self.pipeline_path = os.path.join(os.getcwd(), "experiments", "rand_forest_pipeline.pkl")

    def create_pipeline(self, use_config: bool) -> Pipeline:
        """Создание пайплайна на основе RandomForestRegressor"""
        # Получаем параметры
        if use_config:
            try:
                params = {
                    'n_estimators': self.config.getint("RAND_FOREST", "n_estimators"),
                    'criterion': self.config["RAND_FOREST"]["criterion"],
                    'max_depth': self.config.getint("RAND_FOREST", "max_depth"),
                    'min_samples_leaf': self.config.getint("RAND_FOREST", "min_samples_leaf")
                }
            except KeyError: # pragma: no cover
                self.log.error(traceback.format_exc())
                sys.exit(1)
        else:
            params = {'n_estimators': 100, 'criterion': 'poisson', 'max_depth': 18, 'min_samples_leaf': 2}
        
        # Сохранение параметров и пути в конфиг
        self.config["RAND_FOREST"] = {k: str(v) for k, v in params.items()}
        self.config["RAND_FOREST"]['path'] = self.pipeline_path
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)

        # Создание препроцессора
        preprocessor = ColumnTransformer(transformers=[
            ('ord_enc', OrdinalEncoder(), self.ordinal_columns),
            ('one_hot', OneHotEncoder(drop='first', dtype='int'), self.categorical_columns),
            ('scaler', MinMaxScaler(), self.numeric_columns)
        ])

        # Создание пайплайна
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('model', RandomForestRegressor(**params, random_state=42))
        ])

        return pipeline

    def train_and_evaluate(self, pipeline: Pipeline, predict: bool = True):
        """Обучение и тестирование пайплайна"""
        try:
            pipeline.fit(self.X_train, self.y_train)
            self.log.info("Пайплайн обучен успешно")
        except Exception: # pragma: no cover
            self.log.error("Ошибка при обучении пайплайна")
            self.log.error(traceback.format_exc())
            sys.exit(1)

        if predict:
            y_pred = pipeline.predict(self.X_test)
            r2 = r2_score(self.y_test, y_pred)
            self.log.info(f"R2 Score: {r2:.4f}")

        self.save_pipeline(pipeline)

    def save_pipeline(self, pipeline: Pipeline):
        """Сохранение пайплайна"""
        with open(self.pipeline_path, 'wb') as f:
            pickle.dump(pipeline, f)
        self.log.info(f'Пайплайн сохранён в {self.pipeline_path}')


if __name__ == "__main__": # pragma: no cover
    forest_pipeline = ForestPipelineModel()
    pipeline = forest_pipeline.create_pipeline(use_config=False)
    forest_pipeline.train_and_evaluate(pipeline, predict=True)
