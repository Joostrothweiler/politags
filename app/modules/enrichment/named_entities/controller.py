import logging

from app.models.models import Article
from app.modules.enrichment.named_entities.disambiguation import disambiguate_named_entities
from app.modules.enrichment.named_entities.recognition import recognize_named_entities

logger = logging.getLogger('named_entities')
nlp = None

def extract_disambiguated_named_entities(article: Article, document: dict):
    """
    Extract information from the article, more specifically all named entities linked to knowledge base.
    :param article: article in database.
    :param document: simple document from poliflow.
    """
    recognize_named_entities(article, document)
    parties, politicians = disambiguate_named_entities(article, document)

    return {
        'parties' : parties,
        'politicians' : politicians
    }