from pymongo import MongoClient
from app.config import Config

class DatabaseService:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client.get_database() 
        self.contents = self.db.contents
        self.questions = self.db.questions
        self.users = self.db.users
        self.analytics = self.db.analytics

    def insert_user(self, user):
        return self.users.insert_one(user.to_dict())

    def get_user_by_email(self, email):
        return self.users.find_one({"email": email})

    def insert_content(self, content):
        return self.contents.insert_one(content.to_dict()).inserted_id

    def get_content(self, content_id):
        return self.contents.find_one({"_id": content_id})

    def update_chunks(self, content_id, chunks):
        self.contents.update_one({"_id": content_id}, {"$set": {"chunks": chunks}})

    def insert_question(self, question_data):
        return self.questions.insert_one(question_data).inserted_id
