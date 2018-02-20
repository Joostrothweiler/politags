import logging

from app import db
from app.models.models import *

logger = logging.getLogger('crud')


def find_or_create_article(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    if not article:
        article = Article(id=article_id)
        db.session.add(article)
        db.session.commit()


def store_entity_linking(entity: Entity, linkable_object: object, initial_certainty: float):
    """
    Store the linkings between an entity and a party in the database.
    :param entity: Entity in the database.
    :param linkable_object: Either party or politician object
    :param initial_certainty: Intial certainty score computed based on similarity features and weights.
    """
    linking = EntityLinking.query.filter(EntityLinking.entity == entity).filter(
        EntityLinking.linkable_object == linkable_object).first()

    if linking:
        linking.initial_certainty = initial_certainty
    else:
        linking = EntityLinking(initial_certainty=initial_certainty)
        linking.linkable_object = linkable_object
        entity.linkings.append(linking)
        db.session.add(entity)
    db.session.commit()


def update_entity_count(entity: Entity, count: int):
    entity.count = count
    db.session.commit()


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
