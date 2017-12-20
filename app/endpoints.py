from app.modules.entities.named_entities import process_document
from app.modules.common.utils import translate_doc, convert_to_json
from app.modules.computation.questioning import ask_first_question, process_question
from flask import jsonify
import json


# This file simply handles the API route request and calls the right function.
# Should contain no further logic.

# Route endpoint
def post_article_ner(data):
    doc = convert_to_json(data)
    simple_doc = translate_doc(doc)
    res = process_document(simple_doc)
    return jsonify(res)


# Handling the question generation/querying when poliflw asks for a question.
def post_article_question(data):
    doc = convert_to_json(data)
    simple_doc = translate_doc(doc)
    res = ask_first_question(simple_doc)
    return jsonify(res)


# Handling the response of a question using a post request from poliflw.
def post_question_response(question_id, data):
    doc = convert_to_json(data)
    res = process_question(question_id, doc)
    return jsonify(res)


