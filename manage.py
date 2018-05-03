"""This file sets up a command line manager.

Use "python manage.py" for a list of available commands.
Use "python manage.py runserver" to start the development web server on localhost:5000.
Use "python manage.py runserver --help" for additional runserver options.
"""

from flask_migrate import MigrateCommand
from flask_script import Manager

from app import create_app
from app.commands import *

# Setup Flask-Script with command line commands
manager = Manager(create_app)
manager.add_command('db', MigrateCommand)
manager.add_command('drop_db', DropDbCommand)
manager.add_command('construct_kb', ConstructKbCommand)
manager.add_command('init_kb', InitKbCommand)
manager.add_command('test_ne', TestNeCommand)
manager.add_command('train_clf', TrainClfCommand)
manager.add_command('test_poliflow', TestPoliflowCommand)
manager.add_command('write_ned_training', WriteNedTraining)
manager.add_command('init_topics', InitTopicsCommand)
manager.add_command('quick_verify', QuickVerifyCommand)
manager.add_command('train_topic_clf', TrainTopicClfCommand)
manager.add_command('test_pm', TestPhraseMatcherCommand)
manager.add_command('get_topic_eval', GetTopicEvalCommand)


if __name__ == "__main__":
    manager.run()
