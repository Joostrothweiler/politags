import nl_core_news_sm
from spacy.matcher import PhraseMatcher

from app import db

nlp = nl_core_news_sm.load()

def extract_entities(document):
    sentence = document['description']
    doc = nlp(str(sentence))

    return {
        'ner': ner_response(doc),
        'disambiguid' : disambiguid_entities(ner_response(doc))
    }

def disambiguid_entities(entity_array):
    return [entity_array[0], entity_array[1]]

def process_or_get_entities(article_id):
    return 'entities'

def ner_response(doc):
    res = []
    for ent in doc.ents:
        res.append({'text': ent.text, 'label': ent.label_})

    return res
