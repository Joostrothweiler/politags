import nl_core_news_sm

from app import db
from app.models.models import Article, Entity
from app.modules.common.utils import collection_as_dict, pure_len
from app.modules.entities.disambiguation import politician_disambiguation, party_disambiguation, \
    named_entity_disambiguation
from app.modules.entities.extraction import named_entity_recognition
from app.modules.entities.nlp_model.pipelines import PoliticianRecognizer, PartyRecognizer


def initialize_nlp():
    nlp = nl_core_news_sm.load()
    politician_pipe = PoliticianRecognizer(nlp)
    party_pipe = PartyRecognizer(nlp)
    nlp.add_pipe(politician_pipe, last=True)
    nlp.add_pipe(party_pipe, last=True)
    print(nlp.pipe_names)
    nlp.remove_pipe('tagger')
    nlp.remove_pipe('parser')
    # nlp.remove_pipe('ner')
    return nlp

nlp = initialize_nlp()


def process_document(document):
    article = Article.query.filter(Article.id == document['id']).first()
    if not article:
        print(document['id'])
        article = Article(id = document['id'])
        db.session.add(article)
        db.session.commit()
        extract_knowledge(article, document)
    return return_knowledge(article)


def extract_knowledge(article, document):
    nlp_doc = nlp(str(document['text_description']))
    print(len(nlp_doc.ents))
    entities = named_entity_recognition(article, nlp_doc)
    named_entity_disambiguation(document, entities)


def return_knowledge(article):
    return {'ner': collection_as_dict(article.entities)}