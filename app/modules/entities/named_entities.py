import nl_core_news_sm

from app import db
from app.models.models import Article, Politician, Party
from app.modules.entities.disambiguation import named_entity_disambiguation
from app.modules.entities.extraction import named_entity_recognition
from app.modules.entities.nlp_model.pipelines import PoliticianRecognizer, PartyRecognizer

# Global NLP variable to initialize when necessary
nlp = None

def init_nlp():
    print('Initializing NLP with PhraseMatchers')
    global nlp
    politicians = []
    for politician in Politician.query.distinct(Politician.last_name).limit(100).all():
        if not politician.last_name == '':
            politicians.append(politician.last_name)

    parties = []
    for party in Party.query.all():
        parties.append(party.name)
        if not party.abbreviation == '':
            parties.append(party.abbreviation)

    nlp = nl_core_news_sm.load()
    politician_pipe = PoliticianRecognizer(nlp, politicians)
    party_pipe = PartyRecognizer(nlp, parties)
    nlp.add_pipe(politician_pipe, last=True)
    nlp.add_pipe(party_pipe, last=True)
    nlp.remove_pipe('tagger')
    nlp.remove_pipe('parser')
    nlp.remove_pipe('ner')
    print('NLP Initialized with PhraseMatchers. Pipelines in use: {}'.format(nlp.pipe_names))


def process_document(document):
    # Initialize only if nlp is not yet loaded.
    if nlp == None:
        init_nlp()
    # Make sure the article is in the database.
    article = Article.query.filter(Article.id == document['id']).first()
    if not article:
        article = Article(id = document['id'])
        db.session.add(article)
        db.session.commit()

    extract_information(article, document)
    return return_extracted_information(article)


def extract_information(article, document):
    nlp_doc = nlp(document['text_description'])
    entities = named_entity_recognition(article, nlp_doc)
    named_entity_disambiguation(document, entities)
    db.session.commit()


def return_extracted_information(article):
    parties = []
    politicians = []

    for entity in article.entities:
        for linking in entity.linkings:
            if linking.certainty > 0.6:
                if linking.linkable_type == 'Party':
                    if not linking.linkable_object.as_dict() in parties:
                        parties.append(linking.linkable_object.as_dict())
                elif linking.linkable_type == 'Politician':
                    if not linking.linkable_object.as_dict() in politicians:
                        politicians.append(linking.linkable_object.as_dict())

    return {
        'article_id': article.id,
        'parties': parties,
        'politicians': politicians
    }