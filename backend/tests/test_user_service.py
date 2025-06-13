import unittest
from unittest.mock import MagicMock, patch
from app.services.user_service import UserService
import bcrypt
import jwt
from app.config import Config


class TestUserService(unittest.TestCase):

    @patch('app.services.user_service.DatabaseService')
    def setUp(self, mock_db_service):
        self.mock_collection = MagicMock()
        self.mock_db_instance = mock_db_service.return_value
        self.mock_db_instance.db.users = self.mock_collection

        self.user_service = UserService()

    def test_create_user_already_exists(self):
        self.mock_collection.find_one.return_value = {"email": "test@example.com"}

        result = self.user_service.create_user("Test", "test@example.com", "password123", "student")
        self.assertEqual(result, {"error": "User already exists."})

    @patch('app.services.user_service.bcrypt.hashpw')
    def test_create_user_success(self, mock_hashpw):
        self.mock_collection.find_one.return_value = None
        mock_hashpw.return_value = b"hashedpassword"

        result = self.user_service.create_user("Test", "test@example.com", "password123", "student")
        self.mock_collection.insert_one.assert_called_once()
        self.assertEqual(result, {"message": "User created successfully."})

    def test_authenticate_user_invalid_email(self):
        self.mock_collection.find_one.return_value = None
        result = self.user_service.authenticate_user("notfound@example.com", "any")
        self.assertIsNone(result)

    def test_authenticate_user_wrong_password(self):
        self.mock_collection.find_one.return_value = {
            "email": "test@example.com",
            "password": bcrypt.hashpw(b"otherpassword", bcrypt.gensalt())
        }

        result = self.user_service.authenticate_user("test@example.com", "wrongpassword")
        self.assertIsNone(result)

    def test_authenticate_user_success(self):
        plain_pw = "correctpassword"
        hashed_pw = bcrypt.hashpw(plain_pw.encode(), bcrypt.gensalt())

        user_mock = {
            "_id": "123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "student",
            "password": hashed_pw
        }
        self.mock_collection.find_one.return_value = user_mock

        result = self.user_service.authenticate_user("test@example.com", plain_pw)

        decoded = jwt.decode(result["token"], Config.JWT_SECRET, algorithms=["HS256"])
        self.assertEqual(decoded["email"], "test@example.com")
        self.assertEqual(result["user"]["name"], "Test User")
        self.assertEqual(result["user"]["role"], "student")


if __name__ == '__main__':
    unittest.main()
