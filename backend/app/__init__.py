import yaml

from flask import Flask
from flasgger import Swagger
from app.routes.api_routes import api_bp
from app.routes.auth import auth_bp
from app.routes.analytics_routes import analytics_bp

def create_app():
    app = Flask(__name__)

    # Flasgger config
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }

    # Swagger security definitions for JWT Authorize button
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "RAG Content API",
            "description": "API for uploading content, asking questions, and retrieving Q&A.",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    app.register_blueprint(api_bp, url_prefix='/api/content')
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")

    return app
