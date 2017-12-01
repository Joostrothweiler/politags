from builtins import str
import json
import nl_core_news_sm

nlp = nl_core_news_sm.load()

def extract_named_entities(sentence):
    doc = nlp(str(sentence))
    return json_entities(doc)

def json_entities(doc):
    res = []
    for ent in doc.ents:
        res.append({'entity' : ent.text, 'label' : ent.label_ })

    return json.dumps(res)
