from app.modules.common.utils import get_document_identifier, translate_doc

from app import db
from app.models.models import Article


def ask_first_question(document):
    # PSEUDOCODE
    # get all entities mentioned in article from database
    # find least certain entities_parties or entities_politicians relation
    # query for entity string and party/politician string
    # query for the articles_entities start_pos and end_pos
    # return ["Is {} mentioned here?".format(party/politician string), start_pos, end_pos]

    #get the document identifier
    doc_id = get_document_identifier(document)

    #use the identifier to query for the article
    article = Article.query.filter(Article.id == doc_id).first()

    #if the article is not in the database, stop and return something
    if not article:
        return {'error': 'article not found'}

    first_entity = article.entities[0]

    #find if it is a politician or a party
    politician_certainty = first_entity.politicians[0].certainty
    party_certainty = first_entity.parties[0].certainty

    if politician_certainty > party_certainty:
        question_string = first_entity.politicians[0].full_name
    else:
        question_string = first_entity.parties[0].full_name

    start_pos = first_entity.start_pos
    end_pos = first_entity.end_pos

    return {
        'question': "Is {} mentioned here?".format(question_string),
        'start_pos': start_pos,
        'end_pos': end_pos
    }


def process_question(question_id, data):
    return response

