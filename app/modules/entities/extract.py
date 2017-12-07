import nl_core_news_sm
from spacy.matcher import PhraseMatcher

from app import db
from app.models.models import Article


nlp = nl_core_news_sm.load()

def extract_entities(document):
    # Check article is in db
    article = Article.query.filter(Article.id == document['id']).first()
    # If article is not in db, process and save everything we know
    if not article:
        return process_new_document(document)
    # Otherwise, return what we already know.
    else:
        return fetch_existing_knowledge(article)


def process_new_document(document):
    # First save the new article.
    new_article = Article(id = document['id'])
    db.session.add(new_article)

    doc = nlp(str(document['description']))

    for ent in doc.ents:
        entity = Entity(text = ent.text, label = ent.label_)
        article.entities.append(entity)
        db.session.add(entity)

    db.session.commit()


    return {
        'id': document['id'],
        'ner': ner_response(doc),
        'disambiguid' : disambiguid_entities(ner_response(doc))
    }

def fetch_existing_knowledge(article):
    return 'a'



def disambiguid_entities(entity_array):
    return [entity_array[0], entity_array[1]]

def process_or_get_entities(article_id):
    return 'entities'

def ner_response(doc):
    res = []
    for ent in doc.ents:
        res.append({'text': ent.text, 'label': ent.label_})

    return res
