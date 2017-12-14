from app.modules.entities.named_entities import process_document
from app.modules.common.utils import translate_doc
from app.modules.computation.questioning import ask_first_question, process_question
from flask import jsonify
import json


# This file simply handles the API route request and calls the right function.
# Should contain no further logic.

# Route endpoint
def post_article_ner(document):
    doc = json.loads(document)
    simple_doc = translate_doc(doc)
    res = process_document(simple_doc)
    return jsonify(res)


# Handling the question generation/querying when poliflw asks for a question.
def post_article_question(document):
    doc = json.loads(document)
    simple_doc = translate_doc(doc)
    res = ask_first_question(simple_doc)
    return jsonify(res)


# Handling the response of a question using a post request from poliflw.
def post_question_response(document):
    doc = json.loads(document)
    simple_doc = translate_doc(doc)
    res = process_question(simple_doc)
    return jsonify(res)
