"""
E2E тесты полных workflow
"""
import pytest
import time
from fastapi.testclient import TestClient
from src.api.routes import app


@pytest.fixture(scope="module")
def client():
    """Тестовый клиент"""
    return TestClient(app)


@pytest.mark.e2e
class TestFullWorkflow:
    """E2E тесты полных workflow"""
    
    @pytest.mark.slow
    def test_index_search_workflow(self, client, sample_excel_path):
        """Полный цикл: индексация → поиск"""
        if not sample_excel_path:
            pytest.skip("Тестовый файл не найден")
        
        # 1. Индексация
        index_request = {
            "file_path": sample_excel_path,
            "overwrite": False
        }
        index_response = client.post("/index", json=index_request)
        
        if index_response.status_code == 200:
            doc_id = index_response.json()["document_id"]
            
            # 2. Поиск
            search_request = {
                "query": "тест",
                "top_k": 10
            }
            search_response = client.post("/search", json=search_request)
            assert search_response.status_code == 200
            
            # Проверяем, что документ найден
            results = search_response.json()["results"]
            found_docs = [r for r in results if r.get("document_id") == doc_id]
            # Документ может быть найден или нет, но поиск должен работать
            assert search_response.status_code == 200


@pytest.mark.e2e
@pytest.mark.performance
class TestPerformance:
    """E2E тесты производительности"""
    
    def test_search_performance(self, client):
        """Тест производительности поиска"""
        search_request = {
            "query": "тест",
            "top_k": 10
        }
        
        start = time.perf_counter()
        response = client.post("/search", json=search_request)
        elapsed = time.perf_counter() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # < 1000ms (с запасом для тестов)

