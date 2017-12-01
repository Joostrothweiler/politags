from builtins import str
import json
import nl_core_news_sm
from spacy.matcher import PhraseMatcher

politicians = [
    'Alexander Pechtold',
    'Mark Rutte',
    'Joost Rothweiler',
    'Max van Zoest',
]

nlp = nl_core_news_sm.load()
matcher = PhraseMatcher(nlp.vocab)
patterns = [nlp(text) for text in politicians]
matcher.add('TerminologyList', None, *patterns)


def extract_linked_entities(sentence):
    entity_mentions = extract_named_entities(sentence)

    result = []

    # TODO: Implement actual function.
    for ent in entity_mentions:
        if True:
            result.append(ent)

    return json.dumps(result)


def extract_named_entities(sentence):
    doc = nlp(str(sentence))
    return entities_dict(doc)


def entities_dict(doc):
    res = []
    for ent in doc.ents:
        res.append({'text': ent.text, 'label': ent.label_})

    return res
