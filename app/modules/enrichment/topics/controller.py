from app.modules.enrichment.topics.topic_classifier import classify_and_store_topic


def extract_topics(article, document: dict):
    classify_and_store_topic(article, document)

    return {
        'topics': article.topics
    }
