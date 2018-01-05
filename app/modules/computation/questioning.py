from app import db
from app.models.models import Article
from app import db
from app.models.models import Question, Response, EntityLinking
from random import random


def ask_first_question(document):
    # use the identifier to query for the article
    article = Article.query.filter(Article.id == document['id']).first()

    # if the article is not in the database, stop and return something
    if not article:
        return {
            'error': 'article not found'
        }

    # get article entities
    entities = article.entities

    # use single linked entities to generate
    singlelinked_entities = find_singlelinked_entities(entities)
    doublelinked_entities = find_doublelinked_entities(entities)

    #check if we have any linked entities
    if not singlelinked_entities and not doublelinked_entities:
        return {
            'error': 'no linkings for entities in this article'
        }

    # find all entity linkings for the entities in this article in descending order of certainty
    entity_linkings = find_entity_linkings(doublelinked_entities)
    most_certain_linking = entity_linkings[0]
    least_certain_linking = entity_linkings[-1]

    #assign correct linking
    question_linking = least_certain_linking

    # check if question has already been made for this linking
    database_question = Question.query.filter(Question.questionable_object == question_linking).first()

    # if this question exists, use it
    if database_question:
        question = database_question
    # if not, create a new question
    else:
        question = generate_yesno_question(question_linking, article)


    return {
        'question': question.question_string,
        'question_id': question.id,
        'text': question_linking.entity.text,
        'label': question_linking.entity.label,
        'start_pos': question_linking.entity.start_pos,
        'end_pos': question_linking.entity.end_pos,
        'certainty': question_linking.certainty,
        'possible_answers': question.possible_answers
    }


def find_doublelinked_entities(entities):
    doublelinked_entities = []
    for entity in entities:
        if len(entity.linkings) >= 2:
            doublelinked_entities.append(entity)

    return doublelinked_entities


def find_singlelinked_entities(entities):
    singlelinked_entities = []
    for entity in entities:
        if len(entity.linkings) == 1:
            singlelinked_entities.append(entity)

    return singlelinked_entities


def process_response(question_id, doc):

    response = Response(question_id=question_id, response=doc)
    db.session.add(response)
    db.session.commit()

    return {
        'message': 'response successfully recorded',
        'response': doc
    }


# Find all entity linkings found by Joost's module and sort them by ascending order
def find_entity_linkings(entities):
    entity_ids = [e.id for e in entities]
    entity_linkings = EntityLinking.query.filter(EntityLinking.entity_id.in_(entity_ids)).order_by(
        EntityLinking.certainty.desc()).all()

    return entity_linkings


# this function generates a yes/no question string from an entity
def generate_yesno_question(entity_linking, article):
    if entity_linking.linkable_type == 'Politician':
        politician = entity_linking.linkable_object

        if politician.role:
            question_string = 'Wordt "{}" van "{}", {} in "{}" genoemd in dit artikel?'.format(politician.full_name,
                                                                                               politician.party,
                                                                                               politician.role,
                                                                                               politician.municipality)
        else:
            question_string = 'Wordt "{}" van "{}" in "{}" genoemd in dit artikel?'.format(politician.full_name,
                                                                                           politician.party,
                                                                                           politician.municipality)

        possible_answers = {
            'answers': [

                {
                    'type': 'politician',
                    'id': politician.id,
                    'name': politician.full_name,
                    'party': politician.party,
                    'municipality': politician.municipality,
                    'role': politician.role
                },
                {
                    'type': 'reject',
                    'id': -1
                }
            ]
        }

        question = Question(possible_answers=possible_answers, questionable_object=entity_linking,
                            question_string=question_string, article=article)

    elif entity_linking.linkable_type == 'Party':
        party = entity_linking.linkable_object

        question_string = 'Wordt "{} ({})" uit genoemd in dit artikel?'.format(party.abbreviation, party.name)

        possible_answers = {
            'answers': [
                {
                    'type': 'party',
                    'id': party.id,
                    'name': party.name,
                    'abbreviation': party.abbreviation
                },
                {
                    'type': 'reject',
                    'id': -1
                }
            ]
        }

        question = Question(possible_answers=possible_answers, questionable_object=entity_linking,
                            question_string=question_string, article=article)

    db.session.add(question)
    db.session.commit()

    return question


# def generate_multiple_choice_question(entity_linking, article):
