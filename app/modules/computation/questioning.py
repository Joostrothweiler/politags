from app import db
from app.models.models import Article
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

    [least_certain_entity_index, lowest_certainty] = find_least_certain_entity_index(linked_entities)

    least_certain_entity = linked_entities[least_certain_entity_index]

    yesnoquestion = generate_yesno_question(least_certain_entity)

    start_pos = least_certain_entity.start_pos
    end_pos = least_certain_entity.end_pos

    return {
        'question': yesnoquestion,
        'start_pos': start_pos,
        'end_pos': end_pos,
        'certainty' : lowest_certainty
    }


def process_question(question_id, data):
    return response


#This function gets the string to ask a question
def get_question_string(question):
    return 'klopt dit?'

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
def find_least_certain_entity_index(linked_entities):
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

    return [least_certain_entity_index, lowest_certainty]

#this function generates a yes/no question string from an entity
def generate_yesno_question(linked_entity):
    if linked_entity.politicians:
        question_string = linked_entity.politicians[0].politician.name
    else:
        question_string = linked_entity.parties[0].party.name

    question = 'Is {} mentioned here?'.format(question_string)

    return question


