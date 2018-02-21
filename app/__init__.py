import json
import logging

from flask import Flask, request, render_template, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Instantiate Flask extensions
from app.modules.common.utils import translate_doc
from app.modules.enrichment.controller import fetch_article_enrichment
from app.modules.human_computation.controller import fetch_article_question, post_entity_linking_verification, \
    post_topic_verifications
from app.modules.knowledge_base.controller import fetch_politician_by_id, fetch_party_by_name

from app.local_settings import LOGGING_LEVEL

db = SQLAlchemy()
migrate = Migrate()


# Create the actual application
def create_app(extra_config_settings={}):
    """Create a Flask applicaction.
    """
    # Instantiate Flask
    app = Flask(__name__)
    # Load App Config settings
    # Load common settings from 'app/settings.py' file
    app.config.from_object('app.settings')
    # Load local settings from 'app/local_settings.py'
    app.config.from_object('app.local_settings')
    # Load extra config settings from 'extra_config_settings' param
    app.config.update(extra_config_settings)
    # Set the logging level.
    logging.basicConfig(level=LOGGING_LEVEL)
    # Setup Flask-Extensions -- do this _after_ app config has been loaded
    # Setup Flask-SQLAlchemy
    db.init_app(app)
    # Setup Flask-Migrate
    migrate.init_app(app, db)

    # Register routes
    @app.route('/api/articles/entities', methods=['POST'])
    def article_enrichment():
        document = json.loads(request.data)
        simple_doc = translate_doc(document)
        response = fetch_article_enrichment(simple_doc)
        return jsonify(response)

    @app.route('/api/articles/questions', methods=['POST'])
    def article_question():
        document = json.loads(request.data)
        cookie_id = document['cookie_id']
        simple_doc = translate_doc(document)
        response = fetch_article_question(simple_doc, cookie_id)
        return jsonify(response)

    @app.route('/api/questions/<string:entity_linking_id>', methods=['POST'])
    def entity_linking_verification(param_entity_linking_id):
        document = json.loads(request.data)
        cookie_id = document['cookie_id']
        response_id = document['response_id']
        response = post_entity_linking_verification(document, param_entity_linking_id, cookie_id, response_id)
        return jsonify(response)

    # TODO - article id should either be passed in all routes or none.
    @app.route('/api/topics/<string:article_id>', methods=['POST'])
    def topic_verifications(article_id):
        document = json.loads(request.data)
        cookie_id = document['cookie_id']
        topic_response = document['topic_response']
        response = post_topic_verifications(document, article_id, cookie_id, topic_response)
        return jsonify(response)

    @app.route('/api/politicians/<string:politician_id>', methods=['POST'])
    def politician_by_id(politician_id):
        response = fetch_politician_by_id(politician_id)
        return jsonify(response)

    @app.route('/api/parties/<string:name>', methods=['POST'])
    def party_by_name(name):
        response = fetch_party_by_name(name)
        return jsonify(response)

    @app.route('/article', methods=['GET'])
    def render_html():
        return render_template('index.html')

    return app
