from app.modules.entities.extract import extract_entities
from app.modules.computation.questioning import ask_question, process_question
from flask import jsonify
import json

# This file simply handles the API route request and calls the right function.
# Should contain no further logic.

# Route endpoint
def post_article_ner(document):
    doc = json.loads(document)
    res = extract_entities(doc)
    return jsonify(res)

# Handling the question generation/querying when poliflw asks for a question.
def post_article_question(document):
    doc = json.loads(document)
    res = extract_entities(doc)
    return jsonify(res)

# Handling the response of a question using a post request from poliflw.
def post_question_response(document):
    doc = json.loads(document)
    res = extract_entities(doc)
    return jsonify(res)
