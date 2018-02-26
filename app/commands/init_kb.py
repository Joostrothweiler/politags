import logging

from flask_script import Command

from app.commands.init_topics import init_topics
from app.modules.knowledge_base.update import init_knowledge_base

logger = logging.getLogger('init_kb')


class InitKbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_kb()


def init_kb():
    """ Initialize the database."""
    logger.info('Ready to initialize')
    init_knowledge_base()
    init_topics()
