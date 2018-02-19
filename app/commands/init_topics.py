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
    topics_file = 'data_resources/topics/vng_topics_slug.json'
    topic_json = json.load(open(topics_file))

    logger.info('Inserting topics in database')
    for main in topic_json['topics']:
        # Insert main topic in database
        parent = find_or_create_topic(main['name'], main['slug'], None)
        db.session.commit()
        for sub in main['sub']:
            # insert leaf/sub topics in database.
            find_or_create_topic(sub['name'], sub['slug'], parent.id)
    db.session.commit()

    logger.info('Done')

def find_or_create_topic(new_topic_name: str, new_topic_slug: str, parent_id: int):
    topic = Topic.query.filter(Topic.name == new_topic_name).first()
    if topic:
        topic.slug = new_topic_slug
        topic.parent_id = parent_id
    else:
        topic = Topic(name=new_topic_name, slug=new_topic_slug, parent_id=parent_id)
        db.session.add(topic)
    return topic
