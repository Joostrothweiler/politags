import csv
import logging

from flask_script import Command

from app import db
from app.models.models import Politician, Party, EntityLinking, Entity, Article
from app.modules.knowledge_base.update import update_knowledge_base

logger = logging.getLogger('init_db')


class InitDbCommand(Command):
    """ Initialize the database."""


    def run(self):
        init_db()


def init_db():
    """ Initialize the database."""
    logger.info('Creating tables in database.')
    logger.info('Ready to initialize')
    update_knowledge_base()