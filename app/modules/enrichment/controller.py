

"""
Controller geeft alleen alle API responses
Controller roept zelf geen data aan??

"""
from app.modules.common.crud import find_or_create_article
from app.modules.enrichment.named_entities.controller import extract_disambiguated_named_entities
from app.modules.enrichment.topics.similarity import get_most_similar_topic


def fetch_article_enrichment(document):

    article = find_or_create_article(document['id'])
    named_entities = extract_disambiguated_named_entities(article, document)
    topics = get_most_similar_topic(article, document)

    return {
        'article_id' : article.id,
        'parties' : named_entities['parties'],
        'politicians' : named_entities['politicians'],
        'topics' : topics
    }