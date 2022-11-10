import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
from sqlalchemy.sql.expression import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, selection, no_per_page=QUESTIONS_PER_PAGE):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * no_per_page
    end = start + no_per_page

    resources = [resource.format() for resource in selection]
    paginated_resources = resources[start:end]

    return paginated_resources

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.app_context().push()
    setup_db(app)


    
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    cors =CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Acess-Control-Allow-Headers', 'Content-Type, Authorization, True')
        response.headers.add('Access-Control-Allow-Methods',
        'GET, PUT, POST, DELETE, OPTIONS')
        return response


    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    @cross_origin()
    def get_categories():
        categories = {}
        selection = Category.query.order_by(Category.id).all()
        
        formatted_categories = [category.format() for category in selection]
        for category in formatted_categories:
            categories[str(category['id'])] = category['type']
        
            
        return jsonify(
            {
                "success": True,
                "categories": categories,
                "total_categories": len(Category.query.all())
            }
        )


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    @cross_origin()
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate(request, selection, 10)

        if len(current_questions) == 0:
            abort(404)

        categories = {
            category.id: category.type for category in Category.query.order_by(Category.type).all()
        }
            
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "categories": categories,
                'current_category': []
            }
        )
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
       
        try:
            question = Question.query.get(question_id)
            
            question.delete()
            return jsonify(
                {
                    "success": True,
                    "question_id": question_id
                }
            )
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)

        try:
            new_question = Question(
                question = body.get('question'),
                answer = body.get('answer'),
                difficulty = body.get('difficulty'),
                category = body.get('category')
            )
            new_question.insert()
            
            return jsonify(
                {
                    "success": True,
                    "created": new_question.id,
                    "total_questions": len(Question.query.all())
                }
            )
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        if (not search_term):
            abort(422)
        try:
            
            results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            if results:    
                paginated_questions = paginate(request, results)
                return jsonify(
                    {
                        "success": True,
                        "questions": paginated_questions,
                        "total_search_questions": len(results),
                        "total_questions": len(Question.query.all()),
                    }
                )
            abort(404)
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_in_category(category_id):
        category = Category.query.get(category_id)
        
        if (category is None):
            abort(404)

        try:
            questions = Question.query.filter(Question.category == str(category_id)).all()
            
            paginated_questions = paginate(request, questions)
            return jsonify({
                "category": category_id,
                "questions": paginated_questions,
                "total_category_questions": len(questions),
                "total_questions": len(Question.query.all()),
                "success": True,
            })
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        try:

            body = request.get_json()
            
            category = body.get('quiz_category', None) 
            category_id = int(category['id'])
            previous_questions = body.get('previous_questions', None)
            
            
            # if (len(previous_questions) == 0):
            #     available_questions = Question.query.filter(Question.category == category_id)
            #     # print(available_questions)
            # else:
            #     available_questions = Question.query.filter(~Question.id.in_(previous_questions))

            # if category_id:
            #     available_questions = available_questions.filter(Question.category == category_id)

            
           
            
            # question = available_questions.order_by(func.random()).first()
            if category_id:
                question = Question.query.filter(Question.category == str(category_id)).filter(~Question.id.in_(previous_questions)).order_by(func.random()).first()
            else:
                question = Question.query.filter(~Question.id.in_(previous_questions)).order_by(func.random()).first()
            
            return jsonify({
                "category": category_id,
                "success": True,
                "question": question.format()
            })
        except:
            abort(422)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request_error_handler(error):
        '''
        Error handler for status code 400.
        '''
        return jsonify({
            'success': False,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def resource_not_found_error_handler(error):
        '''
        Error handler for status code 404.
        '''
        return jsonify({
            'success': False,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable_error_handler(error):
        '''
        Error handler for status code 422.
        '''
        return jsonify({
            'success': False,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(500)
    def internal_server_error_handler(error):
        '''
        Error handler for status code 500.
        '''
        return jsonify({
            'success': False,
            'message': 'internal server error'
        }), 500
    return app

