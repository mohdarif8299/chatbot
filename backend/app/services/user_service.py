import bcrypt
import jwt
import datetime
from app.config import Config
from app.services.db_service import DatabaseService

class UserService:
    def __init__(self):
        self.db = DatabaseService()
        self.collection = self.db.db.users

    def create_user(self, name, email, password, role):
        if self.collection.find_one({"email": email}):
            return {"error": "User already exists."}

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = {
            "name": name,
            "email": email,
            "password": hashed_pw,
            "role": role,
            "created": datetime.datetime.utcnow(),
            "updated": datetime.datetime.utcnow()
        }
        self.collection.insert_one(user)
        return {"message": "User created successfully."}

    def authenticate_user(self, email, password):
        user = self.collection.find_one({"email": email})
        if not user:
            return None

        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return None

        payload = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
        return {
            "token": token,
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }

    def get_student_questions(self, student_id):
        
        collection = self.db.questions 

        cursor = collection.find({"user_id": student_id})
        questions = []
        for doc in cursor:
            questions.append({
                "question": doc.get("question"),
                "answer": doc.get("answer"),
                "content_id": doc.get("content_id"),
                "created_at": doc.get("created_at")
            })

        return questions