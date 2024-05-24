import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE,PATCH")
        return response

    # Apply the after_request decorator to all routes
    app.after_request(after_request)

    # Create an endpoint to handle GET requests for all available categories.
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            categories_dict = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'categories': categories_dict
            })
        except Exception as e:
            print(f"Error: {e}")
            abort(500)  # Internal Server Error


    # Create an endpoint to handle GET requests for questions with pagination.
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            if page > QUESTIONS_PER_PAGE:
                # print(f"No questions found for page: {page}")
                abort(404)  # Resource not found

            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]      

            if len(formatted_questions[start:end]) == 0:
                print(f"No questions found for page: {page}")
                abort(404)  # Resource not found

            categories = Category.query.all()
            categories_dict = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_questions': len(formatted_questions),
                'categories': categories_dict,
                'current_category': None
            })
        except Exception as e:
            app.logger.error(f"Error in get_questions: {e}", exc_info=True)
            abort(e.code)  # Internal Server Error


    # Create an endpoint to handle DELETE requests for a question using its ID.
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # Query the question by ID
            question = Question.query.get(question_id)
            if question is None:
                abort(404)  # If the question is not found, return 404 Not Found

            # Delete the question from the database
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except Exception as e:
            print(f"Error: {e}")
            abort(500)  # Internal Server Error

    # Create an endpoint to handle POST requests to add a new question.
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        if not new_question or not new_answer or not new_category or not new_difficulty:
            abort(422)  # Unprocessable Entity if any required field is missing

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id
            })
        except Exception as e:
            print(f"Error: {e}")
            abort(500)  # Internal Server Error

    # Create an endpoint to handle POST requests to get questions based on category.
    @app.route('/categories/<int:category_id>/questions', methods=['POST'])
    def get_questions_by_category(category_id):
        

        if not category_id:
            abort(422)  # Unprocessable Entity if category_id is missing

        try:
            # Query all questions from the specified category
            questions = Question.query.filter(Question.category == str(category_id)).all()
            formatted_questions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': category_id
            })
        except Exception as e:
            print(f"Error: {e}")
            abort(500)  # Internal Server Error

    # Create an endpoint to handle POST requests to get questions based on a search term.
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', '')

        try:
            # Query questions that contain the search term
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            formatted_questions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': None  # This can be modified based on your app's logic
            })
        except Exception as e:
            print(f"Error: {e}")
            abort(500)  # Internal Server Error

    # Create an endpoint to handle POST requests to get questions for the quiz.
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        body = request.get_json()
        previous_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', None)

        if quiz_category is None or 'id' not in quiz_category:
            abort(400)  # Bad Request if quiz_category or category ID is missing

        try:
            if quiz_category['id'] == 0:
                # Query all questions if category id is 0
                questions = Question.query.all()
            else:
                # Query questions from the specified category
                questions = Question.query.filter(Question.category == str(quiz_category['id'])).all()
            
            # Filter out previous questions
            available_questions = [question for question in questions if question.id not in previous_questions]

            # Select a random question
            if len(available_questions) > 0:
                new_question = random.choice(available_questions).format()
            else:
                new_question = None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except Exception as e:
            print(f"Error: {e}")
            abort(500)  # Internal Server Error

    # Error handlers for all expected errors including 400, 404, 422, and 500
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable entity"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app