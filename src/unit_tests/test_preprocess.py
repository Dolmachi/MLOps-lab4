import pytest
import pandas as pd
import os
import sys

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from preprocess import DataMaker

data_maker = DataMaker()

def test_get_data():
    """Тест: Данные должны загружаться и делиться на X и y"""
    assert data_maker.get_data() == True
    assert os.path.isfile(data_maker.X_path), "Файл X_data не создан"
    assert os.path.isfile(data_maker.y_path), "Файл y_data не создан"

def test_split_data():
    """Тест: Данные должны делиться на train/test"""
    assert data_maker.split_data() == True
    assert os.path.isfile(data_maker.train_path[0]), "Train_X не создан"
    assert os.path.isfile(data_maker.train_path[1]), "Train_y не создан"
    assert os.path.isfile(data_maker.test_path[0]), "Test_X не создан"
    assert os.path.isfile(data_maker.test_path[1]), "Test_y не создан"

def test_save_splitted_data():
    """Тест: Должен сохраняться CSV-файл"""
    dummy_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    test_path = "tests/test_dummy.csv"
    
    assert data_maker.save_splitted_data(dummy_df, test_path) == True
    assert os.path.isfile(test_path), "Файл не был создан"
    
    os.remove(test_path)  # Удаляем тестовый файл после проверки
