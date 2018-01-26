from app.models.models import Article
from app import db
from app.models.models import Question, Response, EntityLinking


def generate_question(apidict: dict) -> dict:
    """
    Generate a question for an article in PoliFLW
    :param apidict: POST dict posted by PoliFLW
    :return: the question and its metadata
    """

    article = Article.query.filter(Article.id == apidict['id']).first()
    count_responses = Response.query.count()

    if not article:
        return {
            'error': 'article not found in database',
            'count_responses': count_responses
        }

    entities = article.entities

    entity_linkings = find_linkings(entities)

    if not entity_linkings:
        return {
            'error': 'no linkings for entities in this article'
        }

    generate_linking_questions(entity_linkings, article)

    [next_question_linking, question] = find_next_question(entities)

    if not question:
        return {
            'error': 'no question found for this article',
            'count_responses': count_responses
        }

    return {
        'question': question.question_string_new,
        'question_id': question.id,
        'text': next_question_linking.entity.text,
        'label': next_question_linking.entity.label,
        'start_pos': next_question_linking.entity.start_pos,
        'end_pos': next_question_linking.entity.end_pos,
        'certainty': next_question_linking.updated_certainty,
        'possible_answers': question.possible_answers,
        'count_responses': count_responses
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


def find_next_question(entities: list) -> [EntityLinking, Question]:
    """
    Finds the next question to ask based on a list of entities
    :param entities:
    :return:
    """

    current_maximum_certainty = 0
    next_question_linking = None
    next_question = None

    for entity in entities:
        certain_linkings_count = EntityLinking.query.filter(EntityLinking.entity == entity).filter(
            EntityLinking.initial_certainty == 1).count()

        if certain_linkings_count == 0:
            for linking in entity.linkings:
                question = Question.query.filter(Question.questionable_object == linking).first()
                if question:
                    if linking.updated_certainty >= current_maximum_certainty and linking.updated_certainty < 1:
                        next_question = question
                        next_question_linking = linking
                        current_maximum_certainty = linking.updated_certainty

    return [next_question_linking, next_question]


def generate_linking_questions(entity_linkings: list, article: Article):
    """
    Generates all wanted linking questions and adds them to the database
    :param entity_linkings:
    :param article: article to generate questions for
    :CUTOFF_PARTY_CERTAINTY: the maximum certainty for which we want to ask a question concerning a party
    """

    CUTOFF_PARTY_CERTAINTY = 0.85

    for entity_linking in entity_linkings:
        database_question = Question.query.filter(Question.questionable_object == entity_linking).first()

        if not database_question:
            if entity_linking.linkable_type == 'Politician' or (
                    entity_linking.linkable_type == 'Party' and entity_linking.initial_certainty < CUTOFF_PARTY_CERTAINTY):
                
                question = Question(questionable_object=entity_linking, article=article)
                db.session.add(question)
                db.session.commit()


def process_polar_response(question_id: int, response_id: int):
    """
    Processes a polar response to a question given by a PoliFLW reader
    :param question_id: the question to which the response was given
    :param response_id: the id of the response, either equal to the questioned entity (YES) or -1 (NO)
    :return:
    """
    response_id = int(response_id)

    question = Question.query.filter(Question.id == question_id).first()
    update_linking_certainty(question, response_id)

    response = Response(question_id=question_id, response=response_id)
    db.session.add(response)
    db.session.commit()

    return {
        'message': 'response successfully recorded',
        'response': response_id,
        'right response': question.questionable_object.linkable_object.id
    }


def update_linking_certainty(question: Question, response: Response):
    """
    Updates the certainty of a linking for a given question and response
    :param question: question that was answered
    :param response: response that was given
    :updated_certainty: certainty in the database that we update, this is different from the initial_certainty
    :LEARNING_RATE: the amount with with we want to update the certainty for each response
    """

    LEARNING_RATE = 0.05

    if response == question.questionable_object.linkable_object.id:
        if question.questionable_object.updated_certainty + LEARNING_RATE > 1:
            question.questionable_object.updated_certainty = 1
        else:
            question.questionable_object.updated_certainty += LEARNING_RATE
    else:
        if question.questionable_object.updated_certainty - LEARNING_RATE < 0:
            question.questionable_object.updated_certainty = 0
        else:
            question.questionable_object.updated_certainty -= LEARNING_RATE
