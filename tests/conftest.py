"""
Конфигурация pytest с фикстурами
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from src.database.chroma_manager import ChromaManager
from src.core.embeddings import EmbeddingModel
from src.config.settings import EMBEDDING_MODEL, EMBEDDING_DEVICE


@pytest.fixture(scope="function")
def temp_db():
    """Создает временную БД для тестов"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def chroma_manager(temp_db):
    """Фикстура для ChromaManager с временной БД"""
    return ChromaManager(
        persist_directory=temp_db,
        collection_name="test_collection"
    )


@pytest.fixture(scope="session")
def embedding_model():
    """Фикстура для EmbeddingModel (сессионная для переиспользования)"""
    return EmbeddingModel(
        model_name=EMBEDDING_MODEL,
        device=EMBEDDING_DEVICE
    )


@pytest.fixture
def sample_text():
    """Пример текста для тестирования"""
    return "Это тестовый текст для проверки функциональности обработки документов."


@pytest.fixture
def sample_excel_path():
    """Путь к тестовому Excel файлу"""
    path = Path("docs/testingdocs/Тест-кейсы_ Базовая функциональность.xlsx")
    if path.exists():
        return str(path)
    return None


@pytest.fixture
def sample_pdf_path():
    """Путь к тестовому PDF файлу"""
    path = Path("docs/testingdocs/CloseCheck.pdf")
    if path.exists():
        return str(path)
    return None


@pytest.fixture
def sample_image_path():
    """Путь к тестовому изображению"""
    path = Path("docs/testingdocs/Untitled-1.png")
    if path.exists():
        return str(path)
    return None

