import json
import logging
from flask_script import Command

from app import db
from app.models.models import Topic

logger = logging.getLogger('init_topics')


class InitTopicsCommand(Command):
    def run(self):
        init_topics()


def init_topics():
    logger.info('Ready to initialize topics')

    logger.info('Reading file')
    topics_file = 'data_resources/topics/vng_topics.json'
    topic_json = json.load(open(topics_file))

    logger.info('Inserting topics in database')
    for main in topic_json['topics']:
        # Insert main topic in database
        parent = find_or_create_topic(main['name'], None)
        db.session.commit()
        for sub in main['sub']:
            # insert leaf/sub topics in database.
            find_or_create_topic(sub['name'], parent.id)
    db.session.commit()

    logger.info('Done')

def find_or_create_topic(new_topic_name: str, parent_id: int):
    topic = Topic.query.filter(Topic.name == new_topic_name).first()
    if not topic:
        topic = Topic(name=new_topic_name, parent_id=parent_id)
        db.session.add(topic)
    return topic
