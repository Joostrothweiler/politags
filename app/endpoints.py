from app.modules.entities.named_entities import process_document
from app.modules.common.utils import translate_doc
from app.modules.computation.questioning import generate_question, process_response
from app.modules.knowledge_base.api import find_politician, find_party
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


def post_find_politician(id):
    res = find_politician(id)
    return jsonify(res)

def post_find_party(name):
    res = find_party(name)
    return jsonify(res)


# Handling the question generation/querying when poliflw asks for a question.
def post_article_question(data):
    doc = json.loads(data)
    simple_doc = translate_doc(doc)
    res = generate_question(simple_doc)
    return jsonify(res)


# Handling the response of a question using a post request from poliflw.
def post_question_response(question_id, data):
    doc = json.loads(data)
    res = process_response(question_id, doc)
    return jsonify(res)


