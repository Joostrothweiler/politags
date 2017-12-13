from app import db
from app.models.models import Article
from app import db
from app.models.models import Question
from app.modules.common.utils import collection_as_dict


def ask_first_question(document):
    # PSEUDOCODE
    # get all entities mentioned in article from database
    # find least certain entities_parties or entities_politicians relation
    # query for entity string and party/politician string
    # query for the articles_entities start_pos and end_pos
    # return ["Is {} mentioned here?".format(party/politician string), start_pos, end_pos]

    #use the identifier to query for the article
    article = Article.query.filter(Article.id == document['id']).first()

    #if the article is not in the database, stop and return something
    if not article:
        return {'error': 'article not found'}

    linked_entities = find_linked_entities(article.entities)

    if not linked_entities:
        return {
            'no questions for this article'
        }

    # return collection_as_dict(linked_entities)

    [question_entity, certainty] = find_least_certain_entity(linked_entities)

    # [question_entity, certainty] = find_most_certain_entity(linked_entities)

    question = generate_yesno_question(question_entity)

    return {
        'question': question.question_string,
        'text' : question_entity.text,
        'label' : question_entity.label,
        'start_pos': question_entity.start_pos,
        'end_pos': question_entity.end_pos,
        'certainty' : certainty
    }


def process_question(question_id, data):
    return response

#Find all linked entities of the entities the NER found in the document
def find_linked_entities(entities):
    linked_entities = []
    for entity in entities:
        if entity.politicians:
            linked_entities.append(entity)
        elif entity.parties:
            linked_entities.append(entity)

    return linked_entities

#this function finds the least certain entity in a list of linked entities
def find_least_certain_entity(linked_entities):
    lowest_certainty = 2
    least_certain_entity_index = None

    for index, entity in enumerate(linked_entities):
        for entityparty in entity.parties:
            if entityparty.certainty <= lowest_certainty:
                lowest_certainty = entityparty.certainty
                least_certain_entity_index = index
        for entitypolitician in entity.politicians:
            if entitypolitician.certainty <= lowest_certainty:
                lowest_certainty = entitypolitician.certainty
                least_certain_entity_index = index

    least_certain_entity = linked_entities[least_certain_entity_index]

    return [least_certain_entity, lowest_certainty]


def find_most_certain_entity(linked_entities):
    highest_certainty = 0
    least_certain_entity_index = None

    for index, entity in enumerate(linked_entities):
        for entityparty in entity.parties:
            if entityparty.certainty >= highest_certainty:
                highest_certainty = entityparty.certainty
                most_certain_entity_index = index
        for entitypolitician in entity.politicians:
            if entitypolitician.certainty >= highest_certainty:
                highest_certainty = entitypolitician.certainty
                most_certain_entity_index = index

    most_certain_entity = linked_entities[most_certain_entity_index]

    return [most_certain_entity, highest_certainty]

#this function generates a yes/no question string from an entity
def generate_yesno_question(linked_entity):
    if linked_entity.politicians:
        politician = linked_entity.politicians[0].politician
        question_string = 'Wordt "{}" van "{}" in "{}" genoemd in dit artikel?'.format(politician.full_name, politician.party, politician.municipality)
        question = Question(possible_answers=['Ja', 'Nee'], questionable_type='politician', questionable_id=politician.id, question_string=question_string, article_id=linked_entity.article.id)
    else:
        party = linked_entity.parties[0].party
        question_string = 'Wordt "{}/{}" genoemd in dit artikel?'.format(party.name, party.abbreviation)
        question = Question(possible_answers=['Ja', 'Nee'], questionable_type='party', questionable_id=party.id, question_string=question_string, article_id=linked_entity.article.id)

    db.session.add(question)
    db.session.commit()

    return question
