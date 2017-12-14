import pickle
from flask_script import Command

import nl_core_news_sm

from app.models.models import Politician, Party

class TrainNlpCommand(Command):
    """ Initialize the database."""

    def run(self):
        print('Loading NLP')
        nlp = load_nlp()
        print('Processing politicians and parties')
        process_text_to_docs(nlp)


def load_nlp():
    nlp = nl_core_news_sm.load()
    return nlp

def process_text_to_docs(nlp):
    politicians = []
    for politician in Politician.query.all():
        if not politician.last_name in politicians:
            politicians.append(nlp(politician.last_name))

    parties = []
    for party in Party.query.all():
        if not party.name in parties:
            parties.append(nlp(party.name))
        if not party.abbreviation in parties:
            parties.append(nlp(party.abbreviation))

    save_docs(politicians, 'processed_politician_docs')
    save_docs(parties, 'processed_party_docs')


def save_docs(data, filename):
    with open('app/modules/entities/nlp_model/{}.dat'.format(filename), "wb") as f:
        pickle.dump(data, f)
