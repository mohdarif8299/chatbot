import unittest
from unittest.mock import patch, MagicMock
from app.services.rag_service import RAGService


class TestRAGService(unittest.TestCase):
    @patch('app.services.rag_service.DatabaseService')
    @patch('app.services.rag_service.PineconeService')
    @patch('app.services.rag_service.RedisService')
    @patch('app.services.rag_service.openai.OpenAI')
    def setUp(self, mock_openai, mock_redis, mock_pinecone, mock_db):
        self.mock_db = mock_db.return_value
        self.mock_pinecone = mock_pinecone.return_value
        self.mock_redis = mock_redis.return_value
        self.mock_openai = mock_openai.return_value

        self.rag_service = RAGService()

    @patch('app.services.rag_service.hashlib.md5')
    def test_process_content_with_text_file(self, mock_md5):
        # Arrange
        file_bytes = b"Test file content for processing."
        filename = "test.txt"
        mock_md5.return_value.hexdigest.return_value = "mocked_md5"
        self.rag_service.embed = MagicMock(return_value=[0.1, 0.2, 0.3])

        # Act
        chunks = self.rag_service.process_content(file_bytes, filename)

        # Assert
        self.assertEqual(len(chunks), 1)
        self.mock_pinecone.upsert_vectors.assert_called_once()

    def test_chunk_content(self):
        text = "one two three four five six seven eight nine ten"
        chunks = self.rag_service.chunk_content(text, chunk_size=3)
        self.assertEqual(chunks, ["one two three", "four five six", "seven eight nine", "ten"])

    def test_answer_returns_cached(self):
        self.rag_service.redis.get_cached_answer.return_value = "cached_answer"

        answer = self.rag_service.answer("test question", "content123")
        self.assertEqual(answer, "cached_answer")
        self.rag_service.redis.set_cached_answer.assert_not_called()

    @patch('app.services.rag_service.RAGService.retrieve')
    def test_answer_without_cache(self, mock_retrieve):
        self.rag_service.redis.get_cached_answer.return_value = None
        mock_retrieve.return_value = ["This is context."]
        self.rag_service.client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Generated Answer"))]
        )

        answer = self.rag_service.answer("test question", "content123")
        self.assertEqual(answer, "Generated Answer")
        self.rag_service.redis.set_cached_answer.assert_called_once()


if __name__ == '__main__':
    unittest.main()