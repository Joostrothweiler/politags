import logging
from gensim.models import KeyedVectors

from app import db
from app.models.models import Topic, ArticleTopic, Article

logger = logging.getLogger('similarity')
model = None


def init_model():
    global model
    model = KeyedVectors.load_word2vec_format("data_resources/embeddings/corpus.txt")
    logger.info('Gensim model loaded')


def compute_most_similar_topic(article, document: dict):
    # Initialize only if model is not yet loaded.
    if model == None:
        init_model()

    parent_topic, parent_score = compute_most_similar_parent_topic(document)
    child_topic, child_score = compute_most_similar_child_topic(parent_topic, document)

    insert_article_topic_linking(article, child_topic, child_score)


def compute_most_similar_parent_topic(document: dict):
    most_similar_parent_score = -1
    most_similar_parent_topic = None

    parent_topics = Topic.query.filter(Topic.parent == None).all()

    for parent_topic in parent_topics:
        children_topics = parent_topic.children

        children_topic_names_array = [topic.name for topic in children_topics]
        children_topic_names = ' '.join(children_topic_names_array)
        string_to_compare = parent_topic.name + ' ' + children_topic_names

        score = compute_certainty(document['text_description'], string_to_compare)

        if score > most_similar_parent_score:
            most_similar_parent_score = score
            most_similar_parent_topic = parent_topic

    return most_similar_parent_topic, most_similar_parent_score


def compute_most_similar_child_topic(parent: Topic, document: dict):
    most_similar_child_score = -1
    most_similar_child_topic = None

    child_topics = Topic.query.filter(Topic.parent == parent).all()

    for child_topic in child_topics:
        score = compute_certainty(document['text_description'], child_topic.name)

        if score > most_similar_child_score:
            most_similar_child_score = score
            most_similar_child_topic = child_topic

    return most_similar_child_topic, most_similar_child_score


def compute_certainty(string_a, string_b):
    # Distance should be minimized. So 1 - distance is the score
    return 1 - model.wmdistance(string_a, string_b)


def insert_article_topic_linking(article: Article, topic: Topic, certainty: float):
    existing_linking = ArticleTopic.query.filter(ArticleTopic.article == article).filter(
        ArticleTopic.topic == topic).first()

    if existing_linking:
        existing_linking.initial_certainty = certainty
        existing_linking.updated_certainty = certainty
    else:
        new_linking = ArticleTopic(article=article, topic=topic, initial_certainty=certainty)
        db.session.add(new_linking)
    db.session.commit()
