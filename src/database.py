import yaml
import sys
import os
from pymongo import MongoClient
from logger import Logger


SHOW_LOG = True
logger = Logger(SHOW_LOG).get_logger(__name__)

def get_database():
    """
    Читает параметры подключения к MongoDB из secrets.yml, устанавливает соединение
    и возвращает объект базы данных.
    """
    # Достаем secrets
    base_dir = os.path.dirname(__file__)
    secrets_file_path = os.path.join(base_dir, '..', 'secrets.yml')
    with open(secrets_file_path, "r") as file:
        secrets = yaml.safe_load(file)
    
    try:
        host = secrets['host']
        port = secrets['port']
        user = secrets['user']
        password = secrets['password']
        dbname = secrets['name']
    except KeyError as e:
        logger.error(f"Отсутствует ключ авторизации: {e}")
        sys.exit(1)
    
    # Формируем URI
    uri = f"mongodb://{user}:{password}@{host}:{port}/{dbname}?authSource=admin"
    logger.info(f"MongoDB URI: {uri}")
    
    try:
        client = MongoClient(uri)
        # Проверка подключения
        client.admin.command('ping')
        logger.info(f"Успешное подключение к базе данных '{dbname}' на {host}:{port}")
    except Exception as e: # pragma: no cover
        logger.error("Ошибка подключения к MongoDB", exc_info=True)
        sys.exit(1)
    
    return client[dbname]

if __name__ == "__main__":
    db = get_database()
    logger.info(f"База данных подключена: {db.name}")