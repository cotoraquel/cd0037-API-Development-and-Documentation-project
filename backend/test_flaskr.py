import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://postgres:abc123@localhost:5432/trivia".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_categories(self):
        """Test retrieving categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        """Test retrieving paginated questions"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')  # Assume 1000 is beyond valid range
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        """Test deleting a question"""
        question = Question(question='test question', answer='test answer', difficulty=1, category='1')
        question.insert()

        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question.id)

    def test_create_question(self):
        """Test creating a new question"""
        new_question = {
            'question': 'What is the capital of France?',
            'answer': 'Paris',
            'difficulty': 1,
            'category': '3'
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_422_if_question_creation_fails(self):
        """Test error if question creation fails"""
        new_question = {
            'question': 'What is the capital of France?',
            'answer': '',
            'difficulty': 1,
            'category': '3'
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable entity')

    def test_get_questions_by_category(self):
        """Test retrieving questions by category"""
        res = self.client().post('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], 1)

    def test_search_questions(self):
        """Test searching for questions with a search term"""
        search_term = {'searchTerm': 'title'}
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    def test_get_questions_by_category(self):
        """Test retrieving questions by category"""
        category = Category(type='Science')
        category.insert()
        question = Question(question='What is the boiling point of water?', answer='100 degrees Celsius', difficulty=1, category=category.id)
        question.insert()

        res = self.client().post('/categories/questions', json={'category_id': category.id})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], category.id)

    def test_quiz_questions(self):
        """Test playing quiz by retrieving questions based on category and previous questions"""
        category = Category(type='Science')
        category.insert()
        question1 = Question(question='What is the boiling point of water?', answer='100 degrees Celsius', difficulty=1, category=category.id)
        question2 = Question(question='What is the chemical formula for water?', answer='H2O', difficulty=1, category=category.id)
        question1.insert()
        question2.insert()

        quiz_data = {
            'previous_questions': [question1.id],
            'quiz_category': {'id': category.id}
        }

        res = self.client().post('/quizzes', json=quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'], question1.id)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
