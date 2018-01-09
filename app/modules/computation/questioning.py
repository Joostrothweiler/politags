from app.models.models import Article
from app import db
from app.models.models import Question, Response, EntityLinking


def generate_question(apidoc):
    # use the identifier to query for the article
    article = Article.query.filter(Article.id == apidoc['id']).first()

    # if the article is not in the database, stop and return something
    if not article:
        return {
            'error': 'article not found in database'
        }

    # get article entities
    entities = article.entities

    # find the most certain entity linking
    entity_linkings = find_linkings(entities)

    if not entity_linkings:
        return {
            'error': 'no linkings for entities in this article'
        }

    generate_linking_questions(entity_linkings, article)

    [next_question_linking, question] = find_next_question(entity_linkings)

    if not question:
        return {
            'error': 'no question found for this question'
        }

    return {
        'question': question.question_string,
        'question_id': question.id,
        'text': next_question_linking.entity.text,
        'label': next_question_linking.entity.label,
        'start_pos': next_question_linking.entity.start_pos,
        'end_pos': next_question_linking.entity.end_pos,
        'certainty': next_question_linking.updated_certainty,
        'possible_answers': question.possible_answers
    }


# Find all entity linkings found by Joost's module and sort them by descending order
def find_linkings(entities):
    linkings = []
    for entity in entities:
        for linking in entity.linkings:
            linkings.append(linking)

    # entity_ids = [e.id for e in entities]
    # entity_linkings = EntityLinking.query.filter(EntityLinking.entity_id.in_(entity_ids)).all()

    return linkings


def find_next_question(entity_linkings):
    maximum_certainty = 0

    for linking in entity_linkings:
        question = Question.query.filter(Question.questionable_object == linking).first()
        if question:
            if linking.updated_certainty >= maximum_certainty:
                next_question = question
                next_question_linking = linking
                maximum_certainty = linking.updated_certainty

    return [next_question_linking, next_question]


# this function generates a yes/no question string from an entity
def generate_linking_questions(entity_linkings, article):
    for entity_linking in entity_linkings:
        database_question = Question.query.filter(Question.questionable_object == entity_linking).first()

        if database_question:
            pass

        elif entity_linking.linkable_type == 'Politician':
            politician = entity_linking.linkable_object

            if politician.role and politician.municipality:
                question_string = 'Wordt <strong>{}</strong> van <strong>{}, {}</strong> in <strong>{}</strong> hier genoemd?'.format(politician.full_name,
                                                                                                   politician.party,
                                                                                                   politician.role,
                                                                                                   politician.municipality)
            elif politician.role:
                question_string = 'Wordt <strong>{}, ({})</strong> van <strong>{}</strong> hier genoemd?'.format(politician.full_name,
                                                                                                   politician.party,
                                                                                                   politician.role,)
            else:
                question_string = 'Wordt <strong>{}</strong> van <strong>{}</strong> in <strong>{}</strong> hier genoemd?'.format(politician.full_name,
                                                                                               politician.party,
                                                                                               politician.municipality)

            question = Question(questionable_object=entity_linking,
                                question_string=question_string, article=article)

            db.session.add(question)
            db.session.commit()

        elif entity_linking.linkable_type == 'Party' and entity_linking.initial_certainty < 0.85:
            party = entity_linking.linkable_object

            question_string = 'Wordt <strong>{} ({})</strong> hier genoemd?'.format(party.abbreviation, party.name)

            question = Question(questionable_object=entity_linking,
                                question_string=question_string, article=article)

            db.session.add(question)
            db.session.commit()


def process_response(question_id, response_id):
    response_id = int(response_id)

    # query the question with the question id
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


def update_linking_certainty(question, response):
    learning_rate = 0.1

    if response == question.questionable_object.linkable_object.id:
        if question.questionable_object.updated_certainty + learning_rate > 1:
            question.questionable_object.updated_certainty = 1
        else:
            question.questionable_object.updated_certainty += learning_rate
    else:
        if question.questionable_object.updated_certainty - learning_rate < 0:
            question.questionable_object.updated_certainty = 0
        else:
            question.questionable_object.updated_certainty -= learning_rate
