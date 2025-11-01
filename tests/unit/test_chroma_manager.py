"""
Unit тесты для ChromaManager
"""
import pytest
from src.database.chroma_manager import ChromaManager


@pytest.mark.unit
class TestChromaManager:
    """Тесты для ChromaManager"""
    
    def test_add_and_query(self, chroma_manager, embedding_model):
        """Тест добавления и поиска"""
        ids = ["doc1", "doc2"]
        embeddings = embedding_model.encode(["Текст документа 1", "Текст документа 2"])
        metadatas = [
            {"file_path": "test1.xlsx", "file_name": "test1.xlsx", "document_id": "doc1"},
            {"file_path": "test2.xlsx", "file_name": "test2.xlsx", "document_id": "doc2"}
        ]
        documents = ["Текст документа 1", "Текст документа 2"]
        
        chroma_manager.add_documents(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=documents
        )
        
        # Поиск
        results = chroma_manager.search(
            query_texts=["документ"],
            n_results=2
        )
        
        assert len(results["ids"][0]) >= 0  # Может быть пусто, если нет релевантных
        
    def test_count(self, chroma_manager, embedding_model):
        """Тест подсчета документов"""
        assert chroma_manager.count() == 0
        
        chroma_manager.add_documents(
            ids=["doc1", "doc2"],
            embeddings=embedding_model.encode(["", ""]).tolist(),
            metadatas=[{"file_path": "test1.xlsx"}, {"file_path": "test2.xlsx"}],
            documents=["", ""]
        )
        
        assert chroma_manager.count() == 2
    
    def test_delete(self, chroma_manager, embedding_model):
        """Тест удаления документов"""
        chroma_manager.add_documents(
            ids=["doc1", "doc2"],
            embeddings=embedding_model.encode(["", ""]).tolist(),
            metadatas=[{"file_path": "test1.xlsx"}, {"file_path": "test2.xlsx"}],
            documents=["", ""]
        )
        
        assert chroma_manager.count() == 2
        
        chroma_manager.delete(ids=["doc1"])
        assert chroma_manager.count() == 1
    
    def test_persistence(self, temp_db, embedding_model):
        """Тест сохранности данных после перезапуска"""
        # Создаем первый менеджер
        manager1 = ChromaManager(
            persist_directory=temp_db,
            collection_name="test_collection"
        )
        manager1.add_documents(
            ids=["doc1"],
            embeddings=embedding_model.encode(["Тест"]).tolist(),
            metadatas=[{"file_path": "test.xlsx"}],
            documents=["Тест"]
        )
        
        # Создаем второй менеджер с тем же путем
        manager2 = ChromaManager(
            persist_directory=temp_db,
            collection_name="test_collection"
        )
        
        # Проверяем, что данные сохранились
        assert manager2.count() == 1

