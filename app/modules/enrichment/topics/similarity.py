import pickle
import logging

from app import db
from app.models.models import Topic, ArticleTopic, Article

logger = logging.getLogger('similarity')
classifier = None
transformer = None


def init_models():
    global classifier
    global transformer
    classifier = pickle.load(open('app/modules/enrichment/topics/models/classifier_kamerstukken.sav', 'rb'))
    transformer = pickle.load(open('app/modules/enrichment/topics/models/transformer_kamerstukken.sav', 'rb'))
    logger.info('Topics classifier loaded from desk.')


def compute_most_similar_topic(article, document: dict):
    # Initialize only if model is not yet loaded.
    if classifier == None or transformer == None:
        init_models()

    topic, certainty = predict_article_topic(document)
    insert_article_topic_linking(article, topic, certainty)


def predict_article_topic(document: dict):
    X_tfidf = transformer.transform([document['text_description']])
    # The label used for prediction is the slug of the topic.
    topic_classifier_name = classifier.predict(X_tfidf)[0]
    # Return the maximum probability found - this should be the probability found for this label.
    topic_certainty = max(classifier.predict_proba(X_tfidf)[0])
    # Find the topic in the database based on the slug returned by the classifier.
    topic = Topic.query.filter(Topic.name == topic_classifier_name).first()
    # Return topic object (None if not found) and certainty.
    return topic, topic_certainty


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
