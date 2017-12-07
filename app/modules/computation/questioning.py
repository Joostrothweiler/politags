from app.modules.common.utils import get_document_identifier, translate_doc

from app import db
from app.models.models import Article

def ask_first_question(document):
    doc_id = get_document_identifier(document)

    article = Article.query.filter(Article.id == doc_id).first()

    if not article:
        return {'error': 'article not found'}

    document_entities = article.entities



    entities = article.entities

    # get all entities mentioned in article from database
    # find least certain entities_parties or entities_politicians relation
    # query for entity string and party/politician string
    # query for the articles_entities start_pos and end_pos
    # return ["Is {} mentioned here?".format(party/politician string), start_pos, end_pos]

    return {
        'question': "Is {} mentioned here?".format('party/politicianstring'),
        'start_pos': 0,
        'end_pos': 0
    }


def process_question(question_id, data):
    return response
