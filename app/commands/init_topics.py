import json
import logging
from flask_script import Command

from app import db
from app.models.models import Topic, ArticleTopic

logger = logging.getLogger('init_topics')


class InitTopicsCommand(Command):
    def run(self):
        # drop_topics()
        init_topics()


# def drop_topics():
#     ArticleTopic.query.delete()
#     Topic.query.filter(Topic.parent_id != None).delete()
#     Topic.query.filter(Topic.parent_id == None).delete()


def init_topics():
    logger.info('Ready to initialize topics')

    logger.info('Reading file')
    topics_file = 'data_resources/topics/kamerstukken/kamerstukken_topics_simple.json'
    topic_json = json.load(open(topics_file))

    logger.info('Inserting topics in database')

    for topic_name in topic_json['topics']:
        find_or_create_topic(topic_name)

    logger.info('Done')

def find_or_create_topic(topic_name : str):
    topic = Topic.query.filter(Topic.name == topic_name).first()
    if not topic:
        topic = Topic(name=topic_name)
        db.session.add(topic)
        db.session.commit()
