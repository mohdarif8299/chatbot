import jwt
from flask import request, jsonify
from functools import wraps
from app.config import Config

class JWTService:
    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            if 'Authorization' in request.headers:
                bearer = request.headers.get('Authorization')
                if bearer and bearer.startswith("Bearer "):
                    token = bearer[7:]

            if not token:
                return jsonify({"error": "Token missing"}), 401

            payload = JWTService.decode_token(token)
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401

            request.user = payload
            return f(*args, **kwargs)
        return decorated
