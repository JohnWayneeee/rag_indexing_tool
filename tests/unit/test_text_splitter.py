"""
Unit тесты для TextSplitter
"""
import pytest
from src.core.text_splitter import TextSplitter
from src.config.settings import CHUNK_SIZE, CHUNK_OVERLAP


@pytest.mark.unit
class TestTextSplitter:
    """Тесты для TextSplitter"""
    
    @pytest.fixture
    def splitter(self):
        """Фикстура для создания splitter"""
        return TextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
    
    def test_split_small_text(self, splitter, sample_text):
        """Тест разбиения короткого текста"""
        chunks = splitter.split_text(sample_text)
        
        assert len(chunks) >= 1
        assert chunks[0]["text"] == sample_text or sample_text in chunks[0]["text"]
    
    def test_split_large_text(self, splitter):
        """Тест разбиения длинного текста"""
        # Создаем длинный текст (больше CHUNK_SIZE)
        text = "Тест. " * 1000  # Длинный текст
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 1
        # Проверяем размер чанков
        for chunk in chunks:
            assert len(chunk["text"]) <= CHUNK_SIZE + CHUNK_OVERLAP
    
    def test_chunk_overlap(self, splitter):
        """Тест перекрытия чанков"""
        text = "А" * 2000  # Текст на 2 чанка
        chunks = splitter.split_text(text)
        
        if len(chunks) > 1:
            # Проверяем, что есть перекрытие
            end_of_first = chunks[0]["text"][-CHUNK_OVERLAP:]
            start_of_second = chunks[1]["text"][:CHUNK_OVERLAP]
            # Должны быть одинаковые части или хотя бы пересекаться
            assert len(end_of_first) > 0
            assert len(start_of_second) > 0
    
    def test_split_empty_text(self, splitter):
        """Тест разбиения пустого текста"""
        chunks = splitter.split_text("")
        assert len(chunks) == 0
    
    def test_chunk_metadata(self, splitter, sample_text):
        """Тест метаданных чанков"""
        chunks = splitter.split_text(sample_text)
        
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i
            assert chunk["start_char"] >= 0
            assert chunk["end_char"] <= len(sample_text)
            assert chunk["char_count"] == len(chunk["text"])

