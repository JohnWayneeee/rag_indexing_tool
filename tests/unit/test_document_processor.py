"""
Unit тесты для DocumentProcessor
"""
import pytest
from pathlib import Path
from src.core.document_processor import DocumentProcessor


@pytest.mark.unit
class TestDocumentProcessor:
    """Тесты для DocumentProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Фикстура для создания процессора"""
        return DocumentProcessor()
    
    def test_process_excel(self, processor, sample_excel_path):
        """Тест обработки Excel файла"""
        if not sample_excel_path:
            pytest.skip("Тестовый Excel файл не найден")
        
        result = processor.process_document(sample_excel_path)
        
        assert result is not None
        assert "file_path" in result
        assert "full_text" in result
        assert len(result["full_text"]) > 0
    
    def test_process_pdf(self, processor, sample_pdf_path):
        """Тест обработки PDF файла"""
        if not sample_pdf_path:
            pytest.skip("Тестовый PDF файл не найден")
        
        result = processor.process_document(sample_pdf_path)
        
        assert result is not None
        assert len(result["full_text"]) > 0
    
    def test_process_nonexistent_file(self, processor):
        """Тест обработки несуществующего файла"""
        result = processor.process_document("nonexistent.xlsx")
        assert result is None
    
    def test_process_image_with_ocr(self, processor, sample_image_path):
        """Тест обработки изображения с OCR"""
        if not sample_image_path:
            pytest.skip("Тестовое изображение не найдено")
        
        result = processor.process_document(sample_image_path)
        
        assert result is not None
        # OCR может вернуть пустой текст, но структура должна быть корректной
        assert "file_path" in result

