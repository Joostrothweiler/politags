import logging

from app import db
from app.models.models import Article, Entity, EntityLinking, ArticleTopic

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


def create_entity_or_increment_count(article: Article, text, label, start_pos, end_pos):
    text = text.strip()

    entity = Entity.query.filter(Entity.article_id == article.id) \
        .filter(Entity.text == text) \
        .filter(Entity.label == label).first()

    if entity:
        update_entity_count(entity, entity.count + 1)
    else:
        entity = Entity(text=text, label=label, start_pos=start_pos, end_pos=end_pos)
        entity.article = article
        db.session.add(entity)
    db.session.commit()


def reset_entity_count(entity: Entity):
    update_entity_count(entity, 0)


def update_entity_count(entity: Entity, count: int):
    entity.count = count
    db.session.commit()