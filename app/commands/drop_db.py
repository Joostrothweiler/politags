import logging
from flask_script import Command

from app import db

logger = logging.getLogger('drop_db')


class DropDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        drop_db()


def drop_db():
    """ Initialize the database."""
    logger.info('Dropping Db.')
    # Recreate the database
    db.drop_all()
    logger.info('Dropped Db.')
