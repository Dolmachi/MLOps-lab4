import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from producer import Producer


@patch("producer.KafkaProducer")
def test_producer_send(mock_kafka):
    # Подменяем KafkaProducer на мок и проверяем, что он вызывается
    mock_instance = MagicMock()
    mock_kafka.return_value = mock_instance

    # Создаём нашего продюсера
    p = Producer()
    p.logger = MagicMock()  # чтобы не падал при логировании

    # Отправляем тестовую нагрузку
    payload = {"foo": "bar"}
    p.send(payload)

    # Проверяем, что именно наш мок отправителя получил вызов с нужными аргументами
    mock_instance.send.assert_called_once_with("predictions", payload)
    # Проверяем, что логгер зафиксировал успешную отправку
    p.logger.info.assert_called_once()