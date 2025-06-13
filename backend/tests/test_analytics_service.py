import unittest
from unittest.mock import MagicMock, patch
from app.services.analytics_service import AnalyticsService

class TestAnalyticsService(unittest.TestCase):

    @patch('app.services.analytics_service.DatabaseService')
    def setUp(self, mock_db_service):
        self.mock_db_instance = mock_db_service.return_value
        self.mock_analytics_collection = self.mock_db_instance.analytics
        self.analytics_service = AnalyticsService()

    def test_get_student_analytics_with_existing_data(self):
        mock_data = {
            "_id": "123",
            "student_id": "student_1",
            "total_contents_uploaded": 5,
            "total_questions_asked": 10,
            "total_answer_length": 500
        }
        self.mock_analytics_collection.find_one.return_value = mock_data

        result = self.analytics_service.get_student_analytics("student_1")

        self.assertEqual(result['total_contents_uploaded'], 5)
        self.assertEqual(result['total_questions_asked'], 10)
        self.assertEqual(result['total_answer_length'], 500)
        self.assertEqual(result["_id"], "123")

    def test_get_student_analytics_with_no_data(self):
        self.mock_analytics_collection.find_one.return_value = None

        result = self.analytics_service.get_student_analytics("student_1")

        self.assertEqual(result['total_contents_uploaded'], 0)
        self.assertEqual(result['total_questions_asked'], 0)
        self.assertEqual(result['total_answer_length'], 0)

    def test_update_on_upload(self):
        self.analytics_service.update_on_upload("student_1")
        self.mock_analytics_collection.update_one.assert_called_with(
            {"student_id": "student_1"},
            {"$inc": {"total_contents_uploaded": 1}},
            upsert=True
        )

    def test_update_on_question(self):
        answer = "This is a sample answer"
        self.analytics_service.update_on_question("student_1", answer)
        self.mock_analytics_collection.update_one.assert_called_with(
            {"student_id": "student_1"},
            {"$inc": {"total_questions_asked": 1, "total_answer_length": len(answer)}},
            upsert=True
        )

if __name__ == '__main__':
    unittest.main()
