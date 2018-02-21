import requests
from datetime import date
from sqlalchemy import and_, Date, cast

from app import db
from app.local_settings import PFL_PASSWORD, PFL_USER
from app.models.models import Article
from app.models.models import EntityLinking, Verification, Topic, ArticleTopic
from app.modules.enrichment.controller import fetch_article_enrichment


def generate_questions(apidict: dict, cookie_id : str) -> dict:
    """
    Generate a question for an article in PoliFLW
    :param apidict: POST dict posted by PoliFLW
    :return: the question and its metadata
    """

    article = Article.query.filter(Article.id == apidict['id']).first()

    if not article:
        fetch_article_enrichment(apidict)
        article = Article.query.filter(Article.id == apidict['id']).first()

    count_verifications = Verification.query.count()
    count_verifications_personal = Verification.query.filter(Verification.cookie_id == cookie_id).count()
    count_verifications_today = Verification.query.filter(and_(Verification.cookie_id == cookie_id, cast(Verification.created_at, Date) == date.today())).count()

    entities = article.entities
    entity_linkings = find_linkings(entities)

    topics = generate_topics_json(article)

    if not entity_linkings:
        return {
            'error': 'no linkings for entities in this article',
            'count_verifications': count_verifications,
            'count_verifications_personal': count_verifications_personal,
            'count_verifications_today': count_verifications_today,
            'topics': topics
        }

    next_question_linking = find_next_question_linking(entities, cookie_id)

    if not next_question_linking:
        return {
            'error': 'no question found for this article',
            'count_verifications': count_verifications,
            'count_verifications_personal': count_verifications_personal,
            'count_verifications_today': count_verifications_today,
            'topics': topics
        }

    return {
        'question': next_question_linking.question_string,
        'question_linking_id': next_question_linking.id,
        'text': next_question_linking.entity.text,
        'label': next_question_linking.entity.label,
        'start_pos': next_question_linking.entity.start_pos,
        'end_pos': next_question_linking.entity.end_pos,
        'certainty': next_question_linking.updated_certainty,
        'possible_answers': next_question_linking.possible_answers,
        'count_verifications': count_verifications,
        'count_verifications_personal': count_verifications_personal,
        'count_verifications_today': count_verifications_today,
        'topics': topics
    }

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


def find_next_question_linking(entities: list, cookie_id) -> EntityLinking:
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
                    if Verification.query.filter(and_(Verification.cookie_id == cookie_id, Verification.verifiable_object == linking)).first() is None:
                        next_question_linking = linking
                        current_maximum_certainty = linking.updated_certainty

    return next_question_linking


def process_entity_verification(apidoc: dict, entity_linking_id: int):
    """
    Processes a polar verification to a question given by a PoliFLW reader
    :param entity_linking_id: the linking to which the verification was given
    :param apidoc: the apidoc of the verification, either equal to the questioned entity (YES) or -1 (NO)
    :return:
    """

    answer_id = int(apidoc["response_id"])
    cookie_id = apidoc["cookie_id"]

    entity_linking = EntityLinking.query.filter(EntityLinking.id == entity_linking_id).first()
    update_linking_certainty(entity_linking, answer_id)

    verification = Verification(verifiable_object=entity_linking, response=answer_id, cookie_id=cookie_id)
    db.session.add(verification)
    db.session.commit()

    return {
        'message': 'response successfully recorded',
        'response': answer_id,
        'cookie_id': cookie_id,
        'ground truth': entity_linking.linkable_object.id
    }


def process_topic_verification(article_id: str, cookie_id:str, topic_response: dict):
    """
    Processes a topic verification given by a PoliFLW reader
    :param article_id: the id of the article the reader was reading
    :param apidoc: the apidoc of the verification
    :return:
    """

    for topic in topic_response:
        articleTopic = ArticleTopic.query.filter(and_(ArticleTopic.article_id == article_id, ArticleTopic.topic_id == topic["id"])).first()

        if not articleTopic:
            articleTopic = ArticleTopic(article_id=article_id, topic_id=topic["id"], initial_certainty=0.75)
            db.session.add(articleTopic)
            db.session.commit()

        verification = Verification(verifiable_object=articleTopic, response=topic["response"], cookie_id=cookie_id)
        db.session.add(verification)
        db.session.commit()


    return {
        'message': 'topics successfully recorded'
    }



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
    else:
        if entity_linking.updated_certainty - LEARNING_RATE < 0.5:
            entity_linking.updated_certainty = 0
            # add poliFLW call here
            # update_poliflw_entities(article)
        else:
            entity_linking.updated_certainty -= LEARNING_RATE


def update_poliflw_entities(article):
    # fill in correct url here
    url_string = 'https://api.poliflw.nl/v0/combined_index/{}'.format(article.id)
    jsonupdate = return_extracted_information(article)
    requests.post(url_string, jsonupdate, auth=(PFL_USER, PFL_PASSWORD))


def generate_topics_json(article):
    topics = Topic.query.filter(Topic.parent_id is not None).all()
    topicsarray = []
    for topic in topics:
        articletopic = ArticleTopic.query.filter(and_(ArticleTopic.article == article, ArticleTopic.topic == topic)).first()

        selected = False
        if articletopic:
            if articletopic.updated_certainty > 0.5:
                selected = True

        topicobject = {
            "id": topic.id,
            "text": topic.name,
            "selected": selected
        }

        topicsarray.append(topicobject)

    return topicsarray