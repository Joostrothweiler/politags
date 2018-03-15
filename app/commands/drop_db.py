import logging
from flask_script import Command

from app import db
from app.local_settings import PRODUCTION_ENVIRONMENT

logger = logging.getLogger('drop_db')


class DropDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        drop_db()


def drop_db():
    """ Initialize the database."""
    if not PRODUCTION_ENVIRONMENT:
        logger.info('Dropping Db.')
        # Recreate the database
        db.drop_all()
        logger.info('Dropped Db.')
    else:
        logger.info('Not dropping since we are in production.')
