import requests

from app.models.models import Article
from app import db
from app.models.models import EntityLinking, Verification, Topic, ArticleTopic
from app.modules.enrichment.controller import process_document
from sqlalchemy import and_, Date, cast
from app.local_settings import PFL_PASSWORD, PFL_USER
from app.modules.enrichment.controller import enrichment_response
from datetime import date
from app.local_settings import ALWAYS_PROCESS_ARTICLE_AGAIN

def generate_questions(apidict: dict, cookie_id: str) -> dict:
    """
    Generate a question for an article in PoliFLW
    :param apidict: POST dict posted by PoliFLW
    :param cookie_id: cookie_id of the person visiting the website
    :return: the questions and their metadata
    """

    article = Article.query.filter(Article.id == apidict['id']).first()

    if not article or ALWAYS_PROCESS_ARTICLE_AGAIN:
        process_document(apidict)
        article = Article.query.filter(Article.id == apidict['id']).first()

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
        'topic_response': topic_response
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
            EntityLinking.initial_certainty == 1).first()

        if not certain_linking_exists:
            for linking in entity.linkings:
                if linking.updated_certainty >= current_maximum_certainty and 0.5 <= linking.updated_certainty < 1:
                    verification = Verification.query.filter(
                        and_(Verification.cookie_id == cookie_id, Verification.verifiable_object == linking)).first()
                    if verification is None or verification.response is None:
                        next_question_linking = linking
                        current_maximum_certainty = linking.updated_certainty

    return next_question_linking


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


def process_entity_verification(entity_linking_id: int, apidoc: dict):
    """
    Processes a polar verification to a question given by a PoliFLW reader
    :param entity_linking_id: the linking to which the verification was given
    :param apidoc: the api object of the verification, containing useful information
    :return:
    """

    answer_id = int(apidoc["response_id"])
    cookie_id = apidoc["cookie_id"]

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
        'grount truth id': entity_linking.linkable_object.id
    }


def process_topic_verification(article_id: str, apidoc: dict):
    """
    Processes a topic verification given by a PoliFLW reader
    :param article_id: the id of the article the reader was reading
    :param apidoc: the apidoc of the verification
    :return:
    """

    cookie_id = apidoc["cookie_id"]

    topic_response = apidoc["topic_response"]

    for topic in topic_response:
        article_topic = ArticleTopic.query.filter(
            and_(ArticleTopic.article_id == article_id, ArticleTopic.topic_id == topic["id"])).first()

        if not article_topic:
            article_topic = ArticleTopic(article_id=article_id, topic_id=topic["id"], initial_certainty=0,
                                         updated_certainty=1)

            db.session.add(article_topic)
            db.session.commit()

            article_topic = ArticleTopic.query.filter(and_(ArticleTopic.article_id == article_id, ArticleTopic.topic_id == topic["id"])).first()

            verification = Verification(verifiable_object=article_topic, response=topic["response"],
                                        cookie_id=cookie_id)
            db.session.add(verification)
            db.session.commit

        else:
            verification = Verification.query.filter(and_(Verification.verifiable_object == article_topic, Verification.cookie_id == cookie_id)).first()
            verification.response = topic["response"]
            db.session.add(verification)

        update_topic_certainty(article_topic)

        db.session.commit()

    return {
        'message': 'topics successfully recorded',
        'article_topic': article_topic.topic_id
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

    if article_topic.initial_certainty != 0:
        sum_of_verifications += 1

    if sum_of_verifications > 0:
        article_topic.updated_certainty = 1
    else:
        article_topic.updated_certainty = 0


def update_linking_certainty(entity_linking: EntityLinking, response: int):
    """
    Updates the linking for a given question and response
    :param entity_linking: question that was answered
    :param response: response that was given
    :updated_certainty: certainty in the database that we update, this is different from the initial_certainty
    :LEARNING_RATE: the amount with with we want to update the certainty for each response
    """

    LEARNING_RATE = 0.05
    # article = entity_linking.entity.article

    if response == entity_linking.linkable_object.id:
        entity_linking.updated_certainty = min(entity_linking.updated_certainty + LEARNING_RATE, 1)
        # add poliFLW call here
        # update_poliflw_entities(article)
    elif response == -1:
        if entity_linking.updated_certainty - LEARNING_RATE < 0.5:
            entity_linking.updated_certainty = 0
            # add poliFLW call here
            # update_poliflw_entities(article)
        else:
            entity_linking.updated_certainty -= LEARNING_RATE
    else:
        pass


def update_poliflw_entities(article: Article):
    """
    :param article: article to update metadata for
    """

    # fill in correct url here
    url_string = 'https://api.poliflw.nl/v0/combined_index/{}'.format(article.id)
    jsonupdate = enrichment_response(article)
    requests.post(url_string, jsonupdate, auth=(PFL_USER, PFL_PASSWORD))


def generate_topics_json(article: Article, cookie_id: str) -> list:
    """
    generates the topics that belong to an article to be shown in the topic question
    :param article: article
    :return: topiclist for select2
    """

    topics = Topic.query.all()
    topicsarray = []
    for topic in topics:
        articletopic = ArticleTopic.query.filter(
            and_(ArticleTopic.article == article, ArticleTopic.topic == topic)).first()

        selected = False
        if articletopic:

            if articletopic.updated_certainty > 0:
                selected = True

                verification = Verification.query.filter(
                    and_(Verification.verifiable_object == articletopic, cookie_id == cookie_id)).first()

                if not verification:
                    verification = Verification(verifiable_object=articletopic, response=None,
                                                cookie_id=cookie_id)
                    db.session.add(verification)
                    db.session.commit()

        topicobject = {
            "id": topic.id,
            "text": topic.name,
            "selected": selected
        }

        topicsarray.append(topicobject)
        db.session.commit()

    return topicsarray


def find_topic_response(cookie_id: str, article: Article) -> bool:
    """
    Checks if a user has already given a topic response for this article
    :param cookie_id: cookie id for the user
    :param article: article
    :return: boolean if there's a response given by this user
    """
    topic_response = False

    article_topics = article.topics

    user_verifications = Verification.query.filter(and_(Verification.cookie_id == cookie_id, Verification.response != None)).all()

    for user_verification in user_verifications:
        if user_verification.verifiable_object in article_topics:
            topic_response = True

    return topic_response
