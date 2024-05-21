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


    """
    @TODO DONE : Continue with your other app configurations and routes.
    """
    # Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO DONE: Use the after_request decorator to set Access-Control-Allow
    """
    def after_request(response):
        """
        Set Access-Control-Allow headers to allow requests from any origin.
        """
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE,PATCH")
        return response

    # Apply the after_request decorator to all routes
    app.after_request(after_request)

    """@TODO done:
        Create an endpoint to handle GET requests
        for all available categories.
        """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        
        """
        Handle GET requests for all available categories.
        """
        try:
            # Query all categories from the database
            categories = Category.query.all()

            # Convert category data to a dictionary
            categories_dict = {category.id: category.type for category in categories}

            # Return the JSON response
            return jsonify({
                'success': True,
                'categories': categories_dict
            })
        except Exception as e:
            print(f"Error: {e}")
            abort(500)  # Internal Server Error

    """@TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions."""

    @app.route('/questions', methods=['GET'])
    def get_questions():
        """
        Handle GET requests for questions with pagination.
        """
    try:
        # Get the page number from the request argument, defaulting to 1
        page = request.args.get('page', 1, type=int)

        # Calculate start and end slicing
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        # Query all questions from the database
        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]

        # Query all categories
        categories = Category.query.all()
        categories_dict = {category.id: category.type for category in categories}

        # Return the JSON response
        return jsonify({
            'success': True,
            'questions': formatted_questions[start:end],
            'total_questions': len(formatted_questions),
            'categories': categories_dict,
            'current_category': None  # This can be modified based on your app's logic
        })
    except Exception as e:
        print(f"Error: {e}")
        abort(500)  # Internal Server Error


    return app
