from app.modules.entities.extract import extract_entities
from app.modules.computation.questioning import ask_question, process_question
from flask import jsonify

# This file simply handles the API route request and calls the right function.
# Should contain no further logic.

# Route endpoint
def post_article_ner(article_id):
    return jsonify(extract_entities(article_id))

# Handling the question generation/querying when poliflw asks for a question.
def post_article_question(article_id, data):
    return jsonify(ask_question(article_id, data))

# Handling the response of a question using a post request from poliflw.
def post_question_response(question_id, data):
    return jsonify(process_question(question_id, data))
