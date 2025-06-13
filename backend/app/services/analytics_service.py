import datetime
from bson import ObjectId
from app.services.db_service import DatabaseService

class AnalyticsService:
    def __init__(self):
        self.db = DatabaseService()

    def get_student_analytics(self, student_id):
        analytics = self.db.analytics.find_one({"student_id": student_id})

        if not analytics:
            analytics = {}

        default_fields = {
            "total_contents_uploaded": 0,
            "total_questions_asked": 0,
            "total_answer_length": 0
        }

        for key, value in default_fields.items():
            analytics.setdefault(key, value)

        total_questions = analytics['total_questions_asked']
        total_answer_length = analytics['total_answer_length']

        if "_id" in analytics:
            analytics["_id"] = str(analytics["_id"])

        return analytics

    def update_on_upload(self, student_id):
        self.db.analytics.update_one(
            {"student_id": student_id},
            {
                "$inc": {
                    "total_contents_uploaded": 1
                }
            },
            upsert=True
        )

    def update_on_question(self, student_id, answer):
        self.db.analytics.update_one(
            {"student_id": student_id},
            {
                "$inc": {
                    "total_questions_asked": 1,
                    "total_answer_length": len(answer)
                }
            },
            upsert=True
        )
