import pickle
from spacy.matcher import PhraseMatcher
from spacy.tokens.span import Span

def load_docs(filename):
    try:
        with open('app/modules/entities/nlp_model/{}.dat'.format(filename), "rb") as f:
            return pickle.load(f)
    except:
        return []

POLITICIANS = load_docs('processed_politician_docs')
PARTIES = load_docs('processed_politician_docs')


class PoliticianRecognizer(object):
    name = 'politicians'
    def __init__(self, nlp, label='PER'):

        self.label = nlp.vocab.strings[label]

        patterns = POLITICIANS

        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add('POLITICIANS', None, *patterns)

    def __call__(self, doc):
        matches = self.matcher(doc)
        print('Number of matches: {}'.format(len(matches)))
        spans = []

        for _, start, end in matches:
            entity = Span(doc, start, end, label=self.label)
            spans.append(entity)
            doc.ents = list(doc.ents) + [entity]

        for span in spans:
            span.merge()

        return doc

class PartyRecognizer(object):
    name = 'parties'
    def __init__(self, nlp, label='ORG'):

        self.label = nlp.vocab.strings[label]

        patterns = PARTIES
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add('PARTIES', None, *patterns)

    def __call__(self, doc):
        matches = self.matcher(doc)
        print('Number of matches: {}'.format(len(matches)))
        spans = []

        for _, start, end in matches:
            entity = Span(doc, start, end, label=self.label)
            spans.append(entity)
            doc.ents = list(doc.ents) + [entity]

        for span in spans:
            span.merge()

        return doc