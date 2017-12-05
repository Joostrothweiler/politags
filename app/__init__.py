from datetime import datetime
import os

from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy

# Import api route endpoints.
from .endpoints import post_article_ner, post_article_question, post_question_response

# Instantiate Flask extensions
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
    # Setup Flask-Extensions -- do this _after_ app config has been loaded
    # Setup Flask-SQLAlchemy
    db.init_app(app)
    # Setup Flask-Migrate
    migrate.init_app(app, db)
    # Register routes
    @app.route('/api/articles/<string:article_id>/entities', methods=['GET'])
    def articles_entities(article_id):
        return post_article_ner(article_id)

    @app.route('/api/articles/<string:article_id>/questions', methods=['POST'])
    def articles_questions(article_id):
        return post_article_question(article_id)

    @app.route('/api/questions/<string:question_id>', methods=['POST'])
    def questions_response(question_id):
        return post_question_response(question_id, 'RESPONSE = JA') # TODO Fix body. Probably in endpoint controller.

    return app
