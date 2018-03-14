import logging

from flask import Flask, request, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Instantiate Flask extensions

db = SQLAlchemy()
migrate = Migrate()
# Import rest of the app# Import api route endpoints.
from .endpoints import *
from app.local_settings import LOGGING_LEVEL


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
    def articles_entities():
        return post_article_ner(request.data)

    @app.route('/api/politicians/<string:politician_id>', methods=['POST'])
    def politician_by_id(politician_id):
        return post_find_politician(politician_id)

    @app.route('/api/parties/<string:name>', methods=['POST'])
    def party_by_id(name):
        return post_find_party(name)

    @app.route('/api/articles/questions', methods=['POST'])
    def articles_questions():
        return post_article_question(request.data)

    @app.route('/api/counters', methods=['POST'])
    def counters():
        return post_counters(request.data)

    @app.route('/api/questions/<string:entity_linking_id>', methods=['POST'])
    def questions_response(entity_linking_id):
        return post_question_response(entity_linking_id, request.data)

    @app.route('/api/topics/<string:article_id>', methods=['POST'])
    def topics_response(article_id):
        return post_topics_response(article_id, request.data)

    @app.route('/article', methods=['GET'])
    def render_article():
        return render_template('index.html')

    @app.route('/search', methods=['GET'])
    def render_search():
        return render_template('search.html')

    return app
