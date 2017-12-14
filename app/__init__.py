from datetime import datetime
import os

from flask import Flask, request
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
# Instantiate Flask extensions
db = SQLAlchemy()
migrate = Migrate()
# Import rest of the app# Import api route endpoints.
from .endpoints import post_article_ner, post_article_question, post_question_response

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
    @app.route('/api/articles/entities', methods=['POST'])
    def articles_entities():
        return post_article_ner(request.data)

    @app.route('/api/articles/questions', methods=['POST'])
    def articles_questions():
        return post_article_question(request.data)

    @app.route('/api/questions/<string:question_id>', methods=['POST'])
    def questions_response(question_id):
        return post_question_response(question_id, request.data)

    return app
