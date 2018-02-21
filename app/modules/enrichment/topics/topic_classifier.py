import logging
import pickle

from app.models.models import Topic
from app.modules.enrichment.topics.crud import insert_article_topic_linking

logger = logging.getLogger('similarity')
classifier = None
transformer = None


def init_models():
    global classifier
    global transformer
    classifier = pickle.load(open('app/modules/topics/models/classifier.sav', 'rb'))
    transformer = pickle.load(open('app/modules/topics/models/transformer.sav', 'rb'))
    logger.info('Topics classifier loaded from desk.')


def classify_and_store_topic(article, document: dict):
    # Initialize only if model is not yet loaded.
    if classifier == None or transformer == None:
        init_models()

    X_tfidf = transformer.transform([document['text_description']])
    # The label used for prediction is the slug of the topic.
    topic_slug = classifier.predict(X_tfidf)[0]
    # Return the maximum probability found - this should be the probability found for this label.
    topic_certainty = max(classifier.predict_proba(X_tfidf)[0])
    # Find the topic in the database based on the slug returned by the classifier.
    topic = Topic.query.filter(Topic.slug == topic_slug).first()
    # Store linking
    insert_article_topic_linking(article, topic, topic_certainty)
