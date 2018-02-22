import json

from flask import jsonify

from app.modules.common.utils import translate_doc
from app.modules.computation.questioning import generate_questions, process_entity_verification, process_topic_verification
from app.modules.enrichment.controller import process_document
from app.modules.knowledge_base.api import find_politician, find_party


# This file simply handles the API route request and calls the right function.
# Should contain no further logic.

# Route endpoint

def post_article_ner(document):
    """
    Process an article from poliflow and return the named entities to the api.
    :param document: poliflow document
    :return: API named entities in document
    """
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
    cookie_id = doc['cookie_id']
    simple_doc = translate_doc(doc)
    res = generate_questions(simple_doc, cookie_id)
    return jsonify(res)


# Handling the response of a question using a post request from poliflw.
def post_question_response(entity_linking_id, data):
    doc = json.loads(data)
    res = process_entity_verification(entity_linking_id, doc)
    return jsonify(res)


def post_topics_response(article_id, data):
    doc = json.loads(data)
    res = process_topic_verification(article_id, doc)
    return jsonify(res)