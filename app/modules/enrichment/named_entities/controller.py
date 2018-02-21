import logging

from app.models.models import Article
from app.modules.enrichment.named_entities.disambiguation import disambiguate_named_entities
from app.modules.enrichment.named_entities.recognition import recognize_named_entities

logger = logging.getLogger('named_entities')
nlp = None

def extract_disambiguated_named_entities(article: Article, document: dict):
    recognize_named_entities(article, document)
    parties, politicians = disambiguate_named_entities(article, document)

    return {
        'parties' : parties,
        'politicians' : politicians
    }