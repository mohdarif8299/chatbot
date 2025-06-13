# app/utils/rate_limiter.py

from app.config import Config
from app.services.redis_service import RedisService

redis_service = RedisService()

def check_ai_rate_limit(user_id):
    usage = redis_service.increment_api_usage(user_id)
    if usage > Config.AI_RATE_LIMIT:
        raise Exception("AI Rate limit exceeded.")
