import redis
import json
import datetime
from app.config import Config

class RedisService:
    def __init__(self):
        self.client = redis.Redis.from_url(Config.REDIS_URL)

    def get_cached_answer(self, content_id, question):
        key = f"{content_id}:{question}"
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None

    def set_cached_answer(self, content_id, question, answer, expiration=86400):
        key = f"{content_id}:{question}"
        self.client.setex(key, expiration, json.dumps(answer))
    
    def increment_api_usage(self, user_id):
        key = f"ai_usage:{user_id}:{datetime.date.today()}"
        count = self.client.incr(key)
        if count == 1:
            self.client.expire(key, 86400)
        return count

    def get_api_usage(self, user_id):
        key = f"ai_usage:{user_id}:{datetime.date.today()}"
        return int(self.client.get(key) or 0)
