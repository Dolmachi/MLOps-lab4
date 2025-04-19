import os
import sys
import pytest
import configparser
from unittest.mock import patch, MagicMock

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from database import MongoDBConnector

# Создадим "фейковый" конфиг, который поддерживает get и getint
class FakeDBConfig:
    def __init__(self, d):
        self.d = d
    def get(self, key, default=None):
        return self.d.get(key, default)
    def getint(self, key, default=None):
        return int(self.d.get(key, default))

@patch("database.MongoClient")
def test_get_database(mock_mongo):
    """Тестируем возвращение объекта базы"""
    # Подделываем MongoClient, чтобы не ходить в реальную БД
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    # Инициализируем коннектор и подменяем db_config на наш FakeDBConfig
    connector = MongoDBConnector()
    connector.db_config = FakeDBConfig({
        "host": "localhost",
        "port": "27017",
        "user": "fake_user",
        "password": "fake_pass",
        "name": "test_db"
    })
    
    db = connector.get_database()

    # Проверяем, что вернулся именно mock_db
    assert db == mock_db

    # Проверяем, что вызван метод ping
    mock_client.admin.command.assert_called_once_with('ping')
    # Проверяем, что обращались к нужному имени БД
    mock_client.__getitem__.assert_called_once_with("test_db")