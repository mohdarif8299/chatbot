from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app.services.user_service import UserService

auth_bp = Blueprint('auth', __name__)
user_service = UserService()

@auth_bp.route('/signup', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'User Signup',
    'description': 'Create a new user account',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'role': {'type': 'string'}
                },
                'required': ['name', 'email', 'password']
            }
        }
    ],
    'responses': {
        201: {'description': 'User created successfully'},
        400: {'description': 'Missing fields or user already exists'},
        500: {'description': 'Internal server error'}
    }
})
def signup():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "student")

        if not (name and email and password):
            return jsonify({"error": "Missing fields"}), 400

        result = user_service.create_user(name, email, password, role)

        if result.get("error"):
            return jsonify(result), 400

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'User Login',
    'description': 'Authenticate and generate JWT token',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {'description': 'Authenticated successfully'},
        400: {'description': 'Missing fields'},
        401: {'description': 'Invalid credentials'},
        500: {'description': 'Internal server error'}
    }
})
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not (email and password):
            return jsonify({"error": "Missing fields"}), 400

        auth_result = user_service.authenticate_user(email, password)
        if not auth_result:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify(auth_result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@auth_bp.route('/student/<string:student_id>/questions', methods=['GET'])
@swag_from({
    'tags': ['Questions'],
    'summary': 'Get Questions and Answers for Student',
    'description': 'Fetch all questions and answers asked by a student',
    'parameters': [
        {
            'name': 'student_id',
            'in': 'path',
            'required': True,
            'type': 'string'
        }
    ],
    'responses': {
        200: {'description': 'List of questions and answers'},
        404: {'description': 'No questions found'},
        500: {'description': 'Internal server error'}
    }
})
def get_student_questions(student_id):
    try:
        questions = user_service.get_student_questions(student_id)
        if not questions:
            return jsonify({"message": "No questions found"}), 404

        return jsonify({
            "student_id": student_id,
            "questions": questions
        }), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
