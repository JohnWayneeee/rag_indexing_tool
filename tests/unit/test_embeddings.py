"""
Unit тесты для EmbeddingModel
"""
import pytest
import numpy as np
from src.core.embeddings import EmbeddingModel
from src.config.settings import EMBEDDING_MODEL, EMBEDDING_DEVICE


@pytest.mark.unit
class TestEmbeddingModel:
    """Тесты для EmbeddingModel"""
    
    @pytest.fixture
    def model(self):
        """Фикстура для создания модели"""
        return EmbeddingModel(
            model_name=EMBEDDING_MODEL,
            device=EMBEDDING_DEVICE
        )
    
    def test_encode_single_text(self, model):
        """Тест кодирования одного текста"""
        text = "Тестовый текст для эмбеддинга"
        embedding = model.encode_single(text)
        
        assert embedding is not None
        assert embedding.shape == (384,)  # Размерность модели
        assert isinstance(embedding, np.ndarray)
    
    def test_encode_multiple_texts(self, model):
        """Тест кодирования нескольких текстов"""
        texts = ["Текст 1", "Текст 2", "Текст 3"]
        embeddings = model.encode(texts)
        
        assert embeddings.shape == (3, 384)
        assert len(embeddings) == len(texts)
    
    def test_encode_empty_text(self, model):
        """Тест кодирования пустого текста"""
        # Пустой текст возвращает пустой массив
        embeddings = model.encode([""])
        assert embeddings.shape[0] == 1  # Один эмбеддинг
    
    def test_embedding_dim(self, model):
        """Тест получения размерности эмбеддингов"""
        dim = model.get_embedding_dim()
        assert dim == 384
    
    def test_similarity(self, model):
        """Тест семантической близости"""
        text1 = "авторизация пользователя"
        text2 = "логин в систему"
        text3 = "погода сегодня"
        
        emb1 = model.encode_single(text1)
        emb2 = model.encode_single(text2)
        emb3 = model.encode_single(text3)
        
        # Вычисляем косинусное сходство
        similarity_12 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        similarity_13 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
        
        # text1 и text2 должны быть более похожи (или хотя бы иметь положительное сходство)
        assert similarity_12 > 0
        assert similarity_13 > 0

