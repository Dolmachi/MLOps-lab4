import configparser
import sys
import os
from pymongo import MongoClient
from logger import Logger

class MongoDBConnector:
    def __init__(self):
        self.logger = Logger(True).get_logger(__name__)
        self.config = configparser.ConfigParser()
        self.config.read("config_secret.ini")
        self.db_config = self.config['DATABASE']
    
    def get_database(self):
        '''Подключение к базе данных'''
        # Данные для подключения
        host = self.db_config.get('host')
        port = self.db_config.getint('port')
        user = self.db_config.get('user')
        password = self.db_config.get('password')
        dbname = self.db_config.get('name')
        
        try:
            client = MongoClient(f"mongodb://{user}:{password}@{host}:{port}/")
            client.admin.command('ping') # Проверка подключения
            self.logger.info(f"Успешное подключение к базе данных '{dbname}' на {host}:{port}")
        except Exception as e: # pragma: no cover
            self.logger.error("Ошибка подключения к MongoDB", exc_info=True)
            sys.exit(1)
        
        return client[dbname]