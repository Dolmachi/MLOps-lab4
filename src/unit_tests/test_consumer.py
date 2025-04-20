import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from consumer import Consumer


@patch("consumer.KafkaConsumer", return_value=[MagicMock(value={"input": {}, "prediction": 1})])
@patch("consumer.MongoDBConnector")
def test_consumer_run(mock_mongo, mock_kafka):
    mock_db = MagicMock()
    mock_mongo.return_value.get_database.return_value = mock_db

    consumer = Consumer()
    consumer.run()

    mock_db.predictions.insert_one.assert_called_once_with({"input": {}, "prediction": 1})
