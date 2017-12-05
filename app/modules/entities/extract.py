import nl_core_news_sm
from spacy.matcher import PhraseMatcher

nlp = nl_core_news_sm.load()

def extract_entities(article_id):

    sentence = """Alexander Pechtold (Delft, 16 december 1965) is een
    Nederlandse politicus voor Democraten 66 (D66). Sinds 2006 is hij
    namens die partij fractievoorzitter in de Tweede Kamer."""

    doc = nlp(str(sentence))

    return {
        '_id': article_id,
        'ner': ner_response(doc),
        'disambiguid' : disambiguid_entities(ner_response(doc))
    }

def disambiguid_entities(entity_array):
    return [entity_array[0], entity_array[1]]

def ner_response(doc):
    res = []
    for ent in doc.ents:
        res.append({'text': ent.text, 'label': ent.label_})

    return res
