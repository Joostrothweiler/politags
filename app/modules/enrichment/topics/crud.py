import logging

from app import db
from app.models.models import Article, ArticleTopic, Topic

logger = logging.getLogger('crud')

def insert_article_topic_linking(article: Article, topic: Topic, certainty: float):
    existing_linking = ArticleTopic.query.filter(ArticleTopic.article == article).filter(
        ArticleTopic.topic == topic).first()

    if existing_linking:
        existing_linking.initial_certainty = certainty
        existing_linking.updated_certainty = certainty
    elif topic:
        new_linking = ArticleTopic(article=article, topic=topic, initial_certainty=certainty)
        db.session.add(new_linking)
    else:
        logger.error('Topic not found in database based on slug given. Not inserting anything.')

    db.session.commit()
    return ArticleTopic
