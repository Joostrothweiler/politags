from flask_script import Command
from spacy.matcher import PhraseMatcher

import nl_core_news_sm

from app.models.models import Politician


class TrainNlpCommand(Command):
    """ Initialize the database."""

    def run(self):
        initial = load_nlp()
        with_terms = train_nlp(initial)
        save_nlp(with_terms)


def load_nlp():
    # Right now we just want to load from standard Spacy library
    nlp = nl_core_news_sm.load()
    print('Loaded basic nlp model')
    return nlp

def train_nlp(nlp):
    matcher = PhraseMatcher(nlp.vocab)
    terminology_list = []
    for politician in Politician.query.all():
        terminology_list.append(politician.last_name)

    terminology_list.append('joostrothweilerpolitags')

    patterns = [nlp(text) for text in terminology_list]
    matcher.add('TerminologyList', None, *patterns)

    print('Trained nlp model')
    return nlp

def save_nlp(nlp):
    nlp.to_disk('app/modules/entities/nlp_model/nlp_model_politags')
    print('Saved')
