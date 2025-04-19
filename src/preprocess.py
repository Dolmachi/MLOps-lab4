import configparser
import os
import pandas as pd
from logger import Logger
from sklearn.model_selection import train_test_split
import sys
import traceback

TEST_SIZE = 0.2 # Доля тестовой выборки

class DataMaker():
    def __init__(self) -> None: 
        # Создаем объекты логера и конфигуратора
        logger = Logger(True)
        self.config = configparser.ConfigParser()
        self.log = logger.get_logger(__name__)
        self.config.read("config.ini")
        
        # Пути к файлам
        self.project_path = "data"
        self.data_path = os.path.join(self.project_path, "car_price_dataset.csv")
        self.X_path = os.path.join(self.project_path, "Car_X.csv")
        self.y_path = os.path.join(self.project_path, "Car_y.csv")
        self.train_path = [
            os.path.join(self.project_path, "Train_Car_X.csv"),
            os.path.join(self.project_path, "Train_Car_y.csv")
        ]
        self.test_path = [
            os.path.join(self.project_path, "Test_Car_X.csv"),
            os.path.join(self.project_path, "Test_Car_y.csv")
        ]
        
        self.log.info("DataMaker is ready")

    def get_data(self) -> bool:
        """Разделяет данные на X/y и сохраняет в файлы"""
        try:
            dataset = pd.read_csv(self.data_path)
            self.log.info(f"Dataset loaded from {self.data_path}")
        except FileNotFoundError: # pragma: no cover
            self.log.error(traceback.format_exc())
            sys.exit(1)
        
        # Разделяем X и y и сохраняем по файлам
        X = dataset.drop(["Price"], axis=1)
        y = dataset["Price"]
        
        X.to_csv(self.X_path, index=True)
        y.to_csv(self.y_path, index=True)
        
        self.log.info("X and y data is ready")
        self.config["DATA"] = {'X_data': self.X_path, 'y_data': self.y_path}
        return True

    def split_data(self, test_size=TEST_SIZE) -> bool:
        """Разделяет данные на train/test и сохраняет в файлы"""
        self.get_data()
        try:
            X = pd.read_csv(self.X_path, index_col=0)
            y = pd.read_csv(self.y_path, index_col=0)
        except FileNotFoundError: # pragma: no cover
            self.log.error(traceback.format_exc())
            sys.exit(1)
        
        # Разделяем данные на train/test    
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=0)
        
        # Сохраняем train/test
        self.save_splitted_data(X_train, self.train_path[0])
        self.save_splitted_data(y_train, self.train_path[1])
        self.save_splitted_data(X_test, self.test_path[0])
        self.save_splitted_data(y_test, self.test_path[1])
        
        self.config["SPLIT_DATA"] = {
            'X_train': self.train_path[0],
            'y_train': self.train_path[1],
            'X_test': self.test_path[0],
            'y_test': self.test_path[1]
        }
        
        self.log.info("Train and test data is ready")
        
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
            
        return os.path.isfile(self.train_path[0]) and \
            os.path.isfile(self.train_path[1]) and \
            os.path.isfile(self.test_path[0]) and \
            os.path.isfile(self.test_path[1])

    def save_splitted_data(self, df: pd.DataFrame, path: str) -> bool:
        """Сохраняет данные в CSV"""
        df = df.reset_index(drop=True)
        df.to_csv(path, index=True)
        self.log.info(f'{path} is saved')
        return os.path.isfile(path)


if __name__ == "__main__": # pragma: no cover
    data_maker = DataMaker()
    data_maker.split_data()
