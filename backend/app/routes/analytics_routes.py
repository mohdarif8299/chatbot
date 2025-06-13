from flasgger.utils import swag_from
from flask import Blueprint, request, jsonify
from app.services.jwt_service import JWTService
from app.services.analytics_service import AnalyticsService

analytics_bp = Blueprint('api_analytics_student', __name__)
analytics_service = AnalyticsService()

@analytics_bp.route("/student/<string:student_id>", methods=['GET'])
@JWTService.token_required
@swag_from({
    'tags': ['Analytics'],
    'summary': 'Get student analytics',
    'parameters': [
        {
            'name': 'student_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'The student ID whose analytics you want to fetch'
        },
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': "JWT token. Format: Bearer {token}"
        }
    ],
    'responses': {
        200: {
            'description': 'Student analytics fetched successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    '_id': {'type': 'string'},
                    'total_contents_uploaded': {'type': 'integer'},
                    'total_questions_asked': {'type': 'integer'},
                    'total_answer_length': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'Analytics not found'
        },
        500: {
            'description': 'Internal server error'
        }
    },
    'security': [{'Bearer': []}]
})

def get_student_analytics(student_id):
    try:
        analytics = analytics_service.get_student_analytics(student_id)

        if not analytics:
            return jsonify({"error": "Analytics not found"}), 404

        return jsonify(analytics), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500