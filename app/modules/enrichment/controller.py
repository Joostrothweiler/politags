import logging

from app import db
from app.local_settings import ALWAYS_PROCESS_ARTICLE_AGAIN
from app.models.models import Article, EntityLinking, ArticleTopic
from app.modules.enrichment.named_entities.disambiguation import named_entity_disambiguation
from app.modules.enrichment.named_entities.recognition import named_entity_recognition
from app.modules.enrichment.topics.similarity import compute_most_similar_topic
from app.settings import NED_CUTOFF_THRESHOLD, TOPIC_CUTOFF_THRESHOLD

logger = logging.getLogger('named_entities')


def process_document(document: dict) -> dict:
    """
    Process the simple document and return extracted information.
    :param document: simple document from poliflow.
    :return: extracted information as dict.
    """
    # Make sure the article is in the database.
    article = Article.query.filter(Article.id == document['id']).first()
    if not article:
        article = Article(id=document['id'])
        db.session.add(article)
        db.session.commit()
        enrich_article(article, document)
    # Else if it was already in the database but we set the ALWAYS_PROCESS variable to True in local settings, process.
    elif ALWAYS_PROCESS_ARTICLE_AGAIN:
        enrich_article(article, document)

    return enrichment_response(article)


def enrich_article(article: Article, document: dict):
    """
    Extract information from the article, more specifically all named entities linked to knowledge base.
    :param article: article in database.
    :param document: simple document from poliflow.
    """
    named_entity_recognition(article, document)
    named_entity_disambiguation(article, document)
    compute_most_similar_topic(article, document)


def enrichment_response(article: Article) -> dict:
    """
    Return the extracted information as dict to the API.
    :param article: article in database.
    :return: API response as dict.
    """
    parties = []
    politicians = []

    for entity in article.entities:
        # Select only the linking with the highest updated certainty.
        top_linking = EntityLinking.query.filter(EntityLinking.entity_id == entity.id) \
            .order_by(EntityLinking.updated_certainty.desc()).first()

        if top_linking and top_linking.updated_certainty > NED_CUTOFF_THRESHOLD:
            if top_linking.linkable_type == 'Party':
                if not top_linking.linkable_object.as_dict() in parties:
                    parties.append(top_linking.linkable_object.as_dict())
            elif top_linking.linkable_type == 'Politician':
                if not top_linking.linkable_object.as_dict() in politicians:
                    politicians.append(top_linking.linkable_object.as_dict())

    article_topics = ArticleTopic.query.filter(ArticleTopic.article == article).filter(
        ArticleTopic.initial_certainty > TOPIC_CUTOFF_THRESHOLD).all()

    return {
        'article_id': article.id,
        'parties': parties,
        'politicians': politicians,
        'topics': [article_topic.topic.as_dict() for article_topic in article_topics]
    }
