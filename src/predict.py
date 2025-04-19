import argparse
import configparser
from datetime import datetime
import numpy as np
import os
import json
import pandas as pd
from logger import Logger
from sklearn.metrics import r2_score
from pickle import load
import shutil
import sys
import traceback
import yaml

class PipelinePredictor():
    def __init__(self) -> None:
        # Создаем объекты логера и конфигуратора
        logger = Logger(True)
        self.config = configparser.ConfigParser()
        self.log = logger.get_logger(__name__)
        self.config.read("config.ini")
        
        # Путь к пайплайну
        self.pipeline_path = self.config["RAND_FOREST"]["path"]
        
        # Загружаем пайплайн
        try:
            with open(self.pipeline_path, "rb") as f:
                self.pipeline = load(f)
            self.log.info("Пайплайн успешно загружен")
        except FileNotFoundError: # pragma: no cover
            self.log.error("Файл с пайплайном не найден")
            sys.exit(1)

    def predict(self, X_input: pd.DataFrame) -> float:
        """Предсказание через API"""
        return self.pipeline.predict(X_input)
    
    def test(self) -> bool:
        """Тестирование модели без API"""
        # Создаем парсер для аргументов
        parser = argparse.ArgumentParser(description="Predictor")
        # Выбор типа теста:
        # smoke -> быстрая проверка работы модели (Smoke Test)
        # func -> функциональные тесты на готовых JSON-файлах
        parser.add_argument("--test", "-t",
                                 type=str,
                                 help="Тип тестирования (smoke или func)",
                                 default="smoke",
                                 choices=["smoke", "func"])
        
        # Передаем аргументы
        args = parser.parse_args()  # В обычном запуске читаем аргументы
            
        # Smoke test    
        if args.test == "smoke":
            try:
                X = pd.read_csv(self.config["SPLIT_DATA"]["X_test"], index_col=0)
                y = pd.read_csv(self.config["SPLIT_DATA"]["y_test"], index_col=0).values.ravel()
                y_pred = self.pipeline.predict(X)
                r2 = r2_score(y, y_pred)
                self.log.info(f"Smoke test пройден. R2: {r2:.4f}")             
            except Exception: # pragma: no cover
                self.log.error("Ошибка во время smoke теста")
                self.log.error(traceback.format_exc())
                sys.exit(1)
        
        # Functional test
        elif args.test == "func":
            try:
                # Получаем путь к тестовым json
                base_dir= os.path.dirname(os.path.dirname(__file__))  
                tests_path = os.path.join(base_dir, "tests", "test_data")
                
                # Собираем все примеры
                all_X, all_y = [], []
                test_files = os.listdir(tests_path)

                for test in test_files:
                    test_file = os.path.join(tests_path, test)
                    with open(test_file) as f:
                        test_data = json.load(f)

                    X = [test_data["X"]]
                    y = [test_data["y"]["prediction"]]

                    all_X.extend(X)
                    all_y.extend(y)

                all_X_df = pd.DataFrame(all_X)
                all_y = np.array(all_y)

                # Делаем предсказание и оцениваем метрику
                y_pred = self.pipeline.predict(all_X_df)
                r2 = r2_score(all_y, y_pred)
                self.log.info(f"Func tests пройдены. Итоговый R2: {r2:.4f}")

                # Параметры эксперимента
                exp_dir = os.path.join(os.getcwd(), "experiments", f"experiment_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}")
                os.makedirs(exp_dir, exist_ok=True)

                config_data = {
                    "model_params": self.pipeline.named_steps["model"].get_params(),
                    "model_path": self.pipeline_path,
                    "test_data_paths": test_files
                }

                metrics_data = {
                    "R2_score": r2
                }

                # Сохраняем данные эксперимента
                with open(os.path.join(exp_dir, "config.yaml"), 'w') as cfg_f:
                    yaml.safe_dump(config_data, cfg_f, sort_keys=False)

                with open(os.path.join(exp_dir, "metrics.yaml"), 'w') as metrics_f:
                    yaml.safe_dump(metrics_data, metrics_f, sort_keys=False)

                shutil.copy("logfile.log", os.path.join(exp_dir, 'logs.txt'))

                self.log.info(f"Функциональные тесты завершены успешно")

            except Exception: # pragma: no cover
                self.log.error("Ошибка во время функционального теста")
                self.log.error(traceback.format_exc())
                sys.exit(1)

        return True


if __name__ == "__main__": # pragma: no cover
    predictor = PipelinePredictor()
    predictor.test()
