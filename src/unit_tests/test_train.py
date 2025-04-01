import pytest
import os
from sklearn.pipeline import Pipeline
import sys

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from train import ForestPipelineModel


@pytest.fixture
def model():
    """Создаёт объект модели перед каждым тестом"""
    return ForestPipelineModel()

def test_create_pipeline(model):
    """Проверяем, что создаётся пайплайн"""
    pipeline = model.create_pipeline(use_config=False)
    assert isinstance(pipeline, Pipeline), "Пайплайн не создан"
    pipeline = model.create_pipeline(use_config=True)
    assert isinstance(pipeline, Pipeline), "Пайплайн не создан"

def test_train_and_evaluate(model):
    """Проверяем обучение и сохранение пайплайна"""
    pipeline = model.create_pipeline(use_config=False)

    model.train_and_evaluate(pipeline, predict=True)
    assert os.path.isfile(model.pipeline_path), "Файл пайплайна не был создан"
        
def test_save_pipeline(model):
    """Проверяем, что пайплайн сохраняется корректно"""
    pipeline = model.create_pipeline(use_config=False)
    model.pipeline_path = os.path.join(os.getcwd(), "experiments", "dummy_rand_forest.pkl")
    model.save_pipeline(pipeline)

    assert os.path.isfile(model.pipeline_path), "Файл пайплайна не был создан"
    os.remove(model.pipeline_path)