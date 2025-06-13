import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.rag_service import RAGService
from app.services.analytics_service import AnalyticsService
from app.models.models import Content
from app.services.jwt_service import JWTService
from bson import ObjectId
from flasgger import swag_from
from app.utils.rate_limiter import check_ai_rate_limit

api_bp = Blueprint('api_content', __name__)
rag_service = RAGService()
analytics_service = AnalyticsService()

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route("/upload", methods=['POST'])
@JWTService.token_required
@swag_from({
    'tags': ['Content'],
    'summary': 'Upload Content File',
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'File to upload'
        }
    ],
    'responses': {
        201: {'description': 'Content uploaded successfully'},
        400: {'description': 'Bad request'},
        500: {'description': 'Internal server error'}
    },
    'security': [{'Bearer': []}]
})
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        filename = secure_filename(file.filename)

        if not allowed_file(filename):
            return jsonify({'error': 'Unsupported file type. Only PDF and DOCX are allowed.'}), 400

        file_bytes = file.read()

        user_id = request.user.get("user_id")
        content = Content(title=filename, file_path=filename, user_id=user_id)
        content_dict = content.to_dict() 
        content_id = rag_service.db.contents.insert_one(content_dict).inserted_id

        # Process content regardless of PDF/DOCX
        chunks = rag_service.process_content(file_bytes, filename)  
        rag_service.db.update_chunks(content_id, chunks)

        analytics_service.update_on_upload(user_id)

        return jsonify({
            "message": "Content uploaded successfully",
            "data": {
                "content_id": str(content_id),
                "title": filename,
                "user_id": user_id,
                "chunks_uploaded": len(chunks),
                "created_at": datetime.datetime.utcnow().isoformat()
            }
        }), 201

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@api_bp.route("/<string:content_id>/question", methods=['POST'])
@JWTService.token_required
@swag_from({
    'tags': ['Content'],
    'summary': 'Ask Question',
    'parameters': [
        {
            'name': 'content_id',
            'in': 'path',
            'type': 'string',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'question': {'type': 'string'}
                },
                'required': ['question']
            }
        }
    ],
    'responses': {
        200: {'description': 'Question answered and saved successfully'},
        400: {'description': 'Missing question'},
        429: {'description': 'Rate limit exceeded'},
        500: {'description': 'Internal server error'}
    },
    'security': [{'Bearer': []}]
})
def ask(content_id):
    try:
        data = request.get_json()
        question = data.get("question")
        if not question:
            return jsonify({"error": "Question missing"}), 400

        user_id = request.user.get("user_id")

        check_ai_rate_limit(user_id)

        answer = rag_service.answer(question, content_id)

        question_doc = {
            "content_id": content_id,
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "created_at": datetime.datetime.utcnow()
        }

        rag_service.db.questions.insert_one(question_doc)
        analytics_service.update_on_question(user_id, answer)

        return jsonify({
            "message": "Question answered and saved successfully",
            "data": {
                "question": question,
                "answer": answer,
                "user_id": user_id
            }
        }), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@api_bp.route("/<string:content_id>/questions", methods=['GET'])
@JWTService.token_required
@swag_from({
    'tags': ['Content'],
    'summary': 'Get All Questions',
    'parameters': [
        {
            'name': 'content_id',
            'in': 'path',
            'type': 'string',
            'required': True
        }
    ],
    'responses': {
        200: {'description': 'List of all questions'},
        400: {'description': 'Invalid content_id'},
        404: {'description': 'Content not found or unauthorized'},
        500: {'description': 'Internal server error'}
    },
    'security': [{'Bearer': []}]
})
def get_questions(content_id):
    try:
        user_id = request.user.get("user_id")

        try:
            oid = ObjectId(content_id)
        except Exception:
            return jsonify({"error": "Invalid content_id"}), 400

        all_questions = rag_service.db.questions.find({
            "content_id": content_id,
            "user_id": user_id
        })

        questions = list(all_questions)

        for q in questions:
            q["_id"] = str(q["_id"])

        return jsonify({"questions": questions})

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@api_bp.route("/<string:content_id>/top-questions", methods=['GET'])
@JWTService.token_required
@swag_from({
    'tags': ['Content Analytics'],
    'summary': 'Get Top Asked Questions per Content',
    'description': 'Returns most frequently asked questions for a given content.',
    'parameters': [
        {
            'name': 'content_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'The content ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Top questions list',
            'examples': {
                'application/json': {
                    "content_id": "abcd1234",
                    "top_questions": [
                        {"question": "Explain bond energy.", "count": 5},
                        {"question": "What is covalent bonding?", "count": 3}
                    ]
                }
            }
        },
        500: {'description': 'Internal server error'}
    },
    'security': [{'Bearer': []}]
})
def get_top_questions(content_id):
    try:
        pipeline = [
            {"$match": {"content_id": content_id}},
            {"$group": {"_id": "$question", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        results = rag_service.db.questions.aggregate(pipeline)
        data = [{"question": doc["_id"], "count": doc["count"]} for doc in results]

        return jsonify({"content_id": content_id, "top_questions": data}), 200

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
