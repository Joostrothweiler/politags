from app import db
from app.models.models import Article
from app import db
from app.models.models import Question, Response, EntityLinking

def ask_first_question(document):
    # PSEUDOCODE
    # get all entities mentioned in article from database
    # find least certain entities_parties or entities_politicians relation
    # query for entity string and party/politician string
    # query for the articles_entities start_pos and end_pos
    # return ["Is {} mentioned here?".format(party/politician string), start_pos, end_pos]

    # use the identifier to query for the article
    article = Article.query.filter(Article.id == document['id']).first()

    # if the article is not in the database, stop and return something
    if not article:
        return {'error': 'article not found'}

    # find all entity linkings for the entities in this article in ascending order of certainty
    entity_linkings = find_entity_linkings(article.entities)

    # check if there are any, if not, stop
    if not entity_linkings:
        return {
            'no linkings found for entities in this article'
        }

    # select least certain linking (first in the ascending list).
    question_linking = entity_linkings[1]

    # generate a yes/no question for this entity linking
    question = generate_yesno_question(question_linking, article)

    return {
        'question': question.question_string,
        'text': question_linking.entity.text,
        'label': question_linking.entity.label,
        'start_pos': question_linking.entity.start_pos,
        'end_pos': question_linking.entity.end_pos,
        'certainty': question_linking.certainty
    }


def process_question(question_id, doc):
    # assuming the json response is:
    # { 'response' : 'string'}
    response_string = doc['response']

    response = Response(question_id=question_id, response=response_string)
    db.session.add(response)
    db.session.commit()

    return {
        'message': 'response successfully recorded',
        'response': response_string
    }


# Find all entity linkings found by Joost's module and sort them by ascending order
def find_entity_linkings(entities):
    entity_ids = [e.id for e in entities]
    entity_linkings = EntityLinking.query.filter(EntityLinking.entity_id.in_(entity_ids)).order_by(EntityLinking.certainty.asc()).all()

    return entity_linkings


# this function generates a yes/no question string from an entity
def generate_yesno_question(entity_linking, article):
    if entity_linking.linkable_type == 'Politician':
        politician = entity_linking.linkable_object
        question_string = 'Wordt "{}" van "{}" in "{}" genoemd in dit artikel?'.format(politician.full_name,
                                                                                       politician.party,
                                                                                       politician.municipality)
        question = Question(possible_answers=['Ja', 'Nee'], questionable_object=politician,
                            question_string=question_string, article=article)

    elif entity_linking.linkable_type == 'Party':
        party = entity_linking.linkable_object

        question_string = 'Wordt "{}/{}" genoemd in dit artikel?'.format(party.name, party.abbreviation)

        question = Question(possible_answers=['Ja', 'Nee'], questionable_object=party,
                            question_string=question_string, article=article)

    db.session.add(question)
    db.session.commit()

    return question


