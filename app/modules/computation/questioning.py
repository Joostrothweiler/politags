import requests
import logging

from app.models.models import Article
from app import db
from app.models.models import EntityLinking, Verification, Topic, ArticleTopic
from app.modules.enrichment.controller import process_document
from sqlalchemy import and_, Date, cast
from app.modules.enrichment.controller import enrichment_response
from datetime import date
from app.local_settings import ALWAYS_PROCESS_ARTICLE_AGAIN
from app.settings import NED_ENTITY_LEARNING_RATE, NED_QUESTION_CUTOFF_THRESHOLD
from app.local_settings import UPDATE_POLIFLOW_BASED_ON_DB

logger = logging.getLogger('questioning')

def generate_questions(api_doc: dict, cookie_id: str) -> dict:
    """
    Generate a question for an article in PoliFLW
    :param api_doc: POST dict posted by PoliFLW
    :param cookie_id: cookie_id of the person visiting the website
    :return: the questions and their metadata
    """

    article = Article.query.filter(Article.id == api_doc['id']).first()

    if not article or ALWAYS_PROCESS_ARTICLE_AGAIN:
        process_document(api_doc)
        article = Article.query.filter(Article.id == api_doc['id']).first()

    count_verifications = Verification.query.filter(Verification.response != None).count()
    count_verifications_personal = Verification.query.filter(
        and_(Verification.cookie_id == cookie_id, Verification.response != None)).count()
    count_verifications_today = Verification.query.filter(
        and_(Verification.cookie_id == cookie_id, cast(Verification.created_at, Date) == date.today(),
             Verification.response != None)).count()

    entities = article.entities
    entity_linkings = find_linkings(entities)

    topics = generate_topics_json(article, cookie_id)
    topic_response = find_topic_response(cookie_id, article)

    api_response = {
        'count_verifications': count_verifications,
        'count_verifications_personal': count_verifications_personal,
        'count_verifications_today': count_verifications_today,
        'topics': topics,
        'topic_response': topic_response,
        'cookie_id': cookie_id
    }

    if not entity_linkings:
        api_response['error'] = 'no entity linkings for entities in this article'
        return api_response

    next_question_linking = find_next_question_linking(entities, cookie_id)

    if not next_question_linking:
        api_response['error'] = 'no entity question found or left for this article'
        return api_response

    add_verification_to_database(cookie_id, next_question_linking)

    api_response['question'] = next_question_linking.question_string
    api_response['question_linking_id'] = next_question_linking.id
    api_response['text'] = next_question_linking.entity.text
    api_response['label'] = next_question_linking.entity.label
    api_response['start_pos'] = next_question_linking.entity.start_pos
    api_response['end_pos'] = next_question_linking.entity.end_pos
    api_response['certainty'] = next_question_linking.updated_certainty
    api_response['possible_answers'] = next_question_linking.possible_answers

    return api_response


def calculate_verifications(cookie_id: str) -> dict:
    count_verifications = Verification.query.filter(Verification.response != None).count()
    count_verifications_personal = Verification.query.filter(
        and_(Verification.cookie_id == cookie_id, Verification.response != None)).count()
    count_verifications_today = Verification.query.filter(
        and_(Verification.cookie_id == cookie_id, cast(Verification.created_at, Date) == date.today(),
             Verification.response != None)).count()

    api_response = {
        'count_verifications': count_verifications,
        'count_verifications_personal': count_verifications_personal,
        'count_verifications_today': count_verifications_today,
    }

    return api_response


def find_linkings(entities: list) -> list:
    """
    finds all linkings to entities that were saved to the database by the entities module
    :param entities: a list of entities
    :return: a list of all linkings to these entities
    """

    linkings = []
    for entity in entities:
        for linking in entity.linkings:
            linkings.append(linking)

    return linkings


def find_next_question_linking(entities: list, cookie_id: str) -> EntityLinking:
    """
    Finds the next linking to ask a question for based on a list of entities and a cookie
    :param entities: entities in an article
    :param cookie_id: cookie_id of the user reading
    :return: next_question_linking: the linking and next question to ask
    """

    current_maximum_certainty = 0
    next_question_linking = None

    for entity in entities:
        certain_linking_exists = EntityLinking.query.filter(EntityLinking.entity == entity).filter(
            EntityLinking.updated_certainty == 1).first()

        if not certain_linking_exists:
            for linking in entity.linkings:
                if linking.updated_certainty >= current_maximum_certainty and NED_QUESTION_CUTOFF_THRESHOLD < linking.updated_certainty < 1:
                    verification = Verification.query.filter(
                        and_(Verification.cookie_id == cookie_id, Verification.verifiable_object == linking)).first()
                    if verification is None or verification.response is None:
                        next_question_linking = linking
                        current_maximum_certainty = linking.updated_certainty

    return next_question_linking


# FIXME: This can also work for article_topcic verifications, not only for entity_linkings.
def add_verification_to_database(cookie_id: str, entity_linking: EntityLinking):
    """
    Adds a verification to the database for a certain entity linking and cookie_id
    :param cookie_id: the cookie id of the verifier
    :param entity_linking: the linking to which the verification belongs to
    """

    verification = Verification.query.filter(
        and_(Verification.cookie_id == cookie_id, Verification.verifiable_object == entity_linking)).first()
    if not verification:
        verification = Verification(verifiable_object=entity_linking, cookie_id=cookie_id)
        db.session.add(verification)
        db.session.commit()


def process_entity_verification(entity_linking_id: int, api_doc: dict):
    """
    Processes a polar verification to a question given by a PoliFLW reader
    :param entity_linking_id: the linking to which the verification was given
    :param api_doc: the api object of the verification, containing useful information
    :return:
    """

    answer_id = int(api_doc["response_id"])
    cookie_id = api_doc["cookie_id"]

    entity_linking = EntityLinking.query.filter(EntityLinking.id == entity_linking_id).first()
    update_linking_certainty(entity_linking, answer_id)

    verification = Verification.query.filter(
        and_(Verification.verifiable_object == entity_linking, Verification.cookie_id == cookie_id)).first()
    verification.response = answer_id

    db.session.add(verification)
    db.session.commit()

    return {
        'message': 'response successfully recorded',
        'response': answer_id,
        'cookie_id': cookie_id,
        'ground_truth_id': entity_linking.linkable_object.id
    }


def process_topic_verification(article_id: str, api_doc: dict):
    """
    Processes a topic verification given by a PoliFLW reader
    :param article_id: the id of the article the reader was reading
    :param api_doc: the api_doc of the verification
    :return:
    """

    cookie_id = api_doc["cookie_id"]
    topic_response = api_doc["topic_response"]
    topic_id_list = []
    # A topic response contains a list of topics submitted. Loop over these and process each
    for topic in topic_response:
        article_topic = ArticleTopic.query.filter(ArticleTopic.article_id == article_id)\
                                          .filter(ArticleTopic.topic_id == topic["id"])\
                                          .first()
        # If the article_topic already exists, update the verification
        if article_topic:
            verification = Verification.query.filter(Verification.verifiable_object == article_topic)\
                                             .filter(Verification.cookie_id == cookie_id)\
                                             .first()
            # Our system should always have created a verification if the question was presented to the user.
            # This assertion is used to make sure that this verification actually exists. Otherwise we have a bug.
            assert verification
            # Update the verification - set the actual response
            verification.response = topic["response"]
            db.session.add(verification)
            db.session.commit()
        # Otherwise, create a new article_topic and verification
        else:
            article_topic = ArticleTopic(article_id=article_id,
                                         topic_id=topic["id"],
                                         initial_certainty=0,
                                         updated_certainty=1)
            db.session.add(article_topic)
            db.session.commit()

            verification = Verification(verifiable_object=article_topic,
                                        response=topic["response"],
                                        cookie_id=cookie_id)
            db.session.add(verification)
            db.session.commit()

        # Add topic id to topic_id_list for api response
        topic_id_list.append(article_topic.topic_id)
        # Update article_topic certainty in database
        update_topic_certainty(article_topic)

    return {
        'message': 'topics successfully recorded',
        'article_topic': topic_id_list
    }


def update_topic_certainty(article_topic: ArticleTopic):
    """
    Updates a topic's certainty
    :param article_topic: the article_topic linking
    """

    positive_verifications_count = Verification.query.filter(
        and_(Verification.verifiable_object == article_topic, Verification.response == article_topic.topic_id)).count()
    negative_verifications_count = Verification.query.filter(
        and_(Verification.verifiable_object == article_topic, Verification.response == -1)).count()

    sum_of_verifications = positive_verifications_count - negative_verifications_count

    previous_topic_certainty = article_topic.updated_certainty

    if article_topic.initial_certainty != 0:
        sum_of_verifications += 2

    if sum_of_verifications > 0:
        article_topic.updated_certainty = 1.0
    else:
        article_topic.updated_certainty = 0.0

    db.session.add(article_topic)
    db.session.commit()

    # call to PoliFLW to change
    if article_topic.updated_certainty != previous_topic_certainty and UPDATE_POLIFLOW_BASED_ON_DB:
        update_poliflw_article(article_topic.article)


def update_linking_certainty(entity_linking: EntityLinking, response: int):
    """
    Updates the linking for a given question and response
    :param entity_linking: question that was answered
    :param response: response that was given
    :updated_certainty: certainty in the database that we update, this is different from the initial_certainty
    :NED_ENTITY_LEARNING_RATE: the amount with with we want to update the certainty for each response
    """
    article = entity_linking.entity.article

    if response == entity_linking.linkable_object.id:
        entity_linking.updated_certainty = min(entity_linking.updated_certainty + NED_ENTITY_LEARNING_RATE, 1)

        if entity_linking.updated_certainty + NED_ENTITY_LEARNING_RATE >= 1:
            entity_linking.updated_certainty = 1
            disable_remaining_linkings(entity_linking)
        else:
            entity_linking.updated_certainty = entity_linking.updated_certainty + NED_ENTITY_LEARNING_RATE
    elif response == -1:
        if entity_linking.updated_certainty - NED_ENTITY_LEARNING_RATE < 0.01:
            entity_linking.updated_certainty = 0
        else:
            entity_linking.updated_certainty -= NED_ENTITY_LEARNING_RATE

    # Save certainty update to database.
    db.session.add(entity_linking)
    db.session.commit()
    # There is always an update made, so if in production environment we can update poliflow accordingly.
    if UPDATE_POLIFLOW_BASED_ON_DB:
        update_poliflw_article(article)


def disable_remaining_linkings(entity_linking: EntityLinking):
    """
    Disables all remaining entity linkins when one is set to 1 certainty
    :param entity_linking: the confirmed linking
    """
    entity = entity_linking.entity
    linkable_object = entity_linking.linkable_object
    remaining_linkings = EntityLinking.query.filter(
        and_(EntityLinking.entity == entity, EntityLinking.linkable_object != linkable_object)).all()

    for remaining_linking in remaining_linkings:
        remaining_linking.updated_certainty = 0
        db.session.add(remaining_linking)
    db.session.commit()


def generate_topics_json(article: Article, cookie_id: str) -> list:
    """
    generates the topics that belong to an article to be shown in the topic question
    :param article: article
    :return: topiclist for select2
    """

    topics = Topic.query.all()
    topics_array = []
    for topic in topics:
        article_topic = ArticleTopic.query.filter(ArticleTopic.article == article).filter(ArticleTopic.topic == topic).first()

        selected = False
        if article_topic:

            if article_topic.updated_certainty > 0:
                selected = True

                verification = Verification.query.filter(
                    and_(Verification.verifiable_object == article_topic, cookie_id == cookie_id)).first()

                if not verification:
                    verification = Verification(verifiable_object=article_topic, cookie_id=cookie_id)
                    db.session.add(verification)
                    db.session.commit()

        topic_object = {
            "id": topic.id,
            "text": topic.name,
            "selected": selected
        }

        topics_array.append(topic_object)

    return topics_array


def find_topic_response(cookie_id: str, article: Article) -> bool:
    """
    Checks if a user has already given a topic response for this article
    :param cookie_id: cookie id for the user
    :param article: article
    :return: boolean if there's a response given by this user
    """
    topic_response = False
    article_topics = article.topics
    user_verifications = Verification.query.filter(Verification.cookie_id == cookie_id)\
                                           .filter(Verification.response != None)\
                                           .all()

    for user_verification in user_verifications:
        if user_verification.verifiable_object in article_topics:
            topic_response = True

    return topic_response


def update_poliflw_article(article: Article):
    """
    :param article: article to update metadata for
    """
    try:
        url_string = 'https://elasticsearch:9200/pfl_combined_index/item/{}/_update'.format(article.id)
        json_update = enrichment_response(article)
        requests.post(url_string, json_update)
    except requests.exceptions.RequestException as e:
        logger.error('Failed to update poliflow article: {}'.format(e))

