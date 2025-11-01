"""
Интеграционные тесты для API эндпоинтов
"""
import pytest
import tempfile
import shutil
from fastapi.testclient import TestClient
from src.api.routes import app, startup_event
from src.database.chroma_manager import ChromaManager
from src.core.embeddings import EmbeddingModel
from src.services.indexing_service import IndexingService
from src.services.search_service import SearchService
from src.config.settings import EMBEDDING_MODEL, EMBEDDING_DEVICE


@pytest.fixture(scope="module")
def temp_db():
    """Временная БД для тестов"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def initialized_app(temp_db):
    """Инициализирует сервисы для тестов"""
    import src.api.routes as routes_module
    
    # Инициализация сервисов
    embedding_model = EmbeddingModel(
        model_name=EMBEDDING_MODEL,
        device=EMBEDDING_DEVICE
    )
    
    chroma_manager = ChromaManager(
        persist_directory=temp_db,
        collection_name="test_collection"
    )
    
    routes_module.chroma_manager = chroma_manager
    routes_module.embedding_model = embedding_model
    routes_module.indexing_service = IndexingService(
        chroma_manager=chroma_manager,
        embedding_model=embedding_model
    )
    routes_module.search_service = SearchService(
        chroma_manager=chroma_manager,
        embedding_model=embedding_model
    )
    
    yield app
    
    # Очистка
    routes_module.chroma_manager = None
    routes_module.embedding_model = None
    routes_module.indexing_service = None
    routes_module.search_service = None


@pytest.fixture(scope="module")
def client(initialized_app):
    """Фикстура для тестового клиента с инициализированными сервисами"""
    return TestClient(initialized_app)


@pytest.mark.integration
class TestHealthEndpoints:
    """Тесты для эндпоинтов здоровья"""
    
    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "RAG Indexing Tool API"
        assert data["version"] == "1.0.0"
    
    def test_health_check(self, client):
        """Тест health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"]["connected"] == True
    
    def test_status_endpoint(self, client):
        """Тест статуса системы"""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "embedding_model" in data
        assert data["embedding_dim"] == 384
    
    def test_supported_formats(self, client):
        """Тест получения поддерживаемых форматов"""
        response = client.get("/formats")
        assert response.status_code == 200
        data = response.json()
        assert "supported_extensions" in data
        assert "formats" in data
        assert len(data["supported_extensions"]) > 10


@pytest.mark.integration
class TestSearchEndpoints:
    """Тесты для эндпоинтов поиска"""
    
    def test_search_endpoint(self, client):
        """Тест поискового эндпоинта"""
        request = {
            "query": "тест",
            "top_k": 10,
            "min_score": None
        }
        response = client.post("/search", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert "total_results" in data
    
    def test_simple_search_endpoint(self, client):
        """Тест упрощенного поиска"""
        response = client.post("/search/simple", params={"query_text": "тест", "top_k": 10})
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
    
    @pytest.mark.parametrize("top_k", [1, 5, 10, 20])
    def test_search_top_k(self, client, top_k):
        """Тест поиска с различными значениями top_k"""
        request = {
            "query": "тест",
            "top_k": top_k
        }
        response = client.post("/search", json=request)
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= top_k


@pytest.mark.integration
class TestIndexingEndpoints:
    """Тесты для эндпоинтов индексации"""
    
    def test_index_nonexistent_file(self, client):
        """Тест индексации несуществующего файла"""
        request = {
            "file_path": "nonexistent.xlsx",
            "overwrite": False
        }
        response = client.post("/index", json=request)
        assert response.status_code == 404
    
    def test_search_no_results(self, client):
        """Тест поиска без результатов"""
        request = {
            "query": "несуществующий термин xyz123",
            "top_k": 10
        }
        response = client.post("/search", json=request)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["results"], list)
        assert data["total_results"] >= 0

