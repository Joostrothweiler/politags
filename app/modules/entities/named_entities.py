import nl_core_news_sm
import logging

from app import db
from app.models.models import Article, EntityLinking
from app.modules.entities.disambiguation import named_entity_disambiguation
from app.modules.entities.nlp_model.pipelines import PoliticianRecognizer, PartyRecognizer
from app.modules.entities.recognition import named_entity_recognition
from app.settings import NED_CUTOFF_THRESHOLD

logger = logging.getLogger('named_entities')
nlp = None


def init_nlp():
    """
    Initialize the NLP module with PhraseMatcher
    """
    logger.info('NLP Module : Initializing')
    global nlp
    politicians = []
    parties = []
    # for politician in Politician.query.all():
    #     if not politician.last_name == '':
    #         politicians.append(politician.last_name)
    # for party in Party.query.all():
    #     parties.append(party.name)
    #     if not party.abbreviation == '':
    #         parties.append(party.abbreviation)
    nlp = nl_core_news_sm.load()
    politician_pipe = PoliticianRecognizer(nlp, politicians)
    party_pipe = PartyRecognizer(nlp, parties)
    nlp.add_pipe(politician_pipe, last=True)
    nlp.add_pipe(party_pipe, last=True)
    nlp.remove_pipe('tagger')
    nlp.remove_pipe('parser')
    logger.info('NLP Module : Initialized. Pipelines in use: {}'.format(nlp.pipe_names))


def process_document(document: dict) -> dict:
    """
    Process the simple document and return extracted information.
    :param document: simple document from poliflow.
    :return: extracted information as dict.
    """
    # Initialize only if nlp is not yet loaded.
    if nlp == None:
        init_nlp()
    # Make sure the article is in the database.
    article = Article.query.filter(Article.id == document['id']).first()
    if not article:
        article = Article(id=document['id'])
        db.session.add(article)
        db.session.commit()

    extract_information(article, document)
    return return_extracted_information(article)


def extract_information(article: Article, document: dict):
    """
    Extract information from the article, more specifically all named entities linked to knowledge base.
    :param article: article in database.
    :param document: simple document from poliflow.
    """
    nlp_doc = nlp(document['text_description'])
    entities = named_entity_recognition(article, nlp_doc)
    named_entity_disambiguation(entities, document)
    db.session.commit()


def return_extracted_information(article: Article) -> dict:
    """
    Return the extracted information as dict to the API.
    :param article: article in database.
    :return: API response as dict.
    """
    parties = []
    politicians = []

    for entity in article.entities:
        # Select only the linking with the highest updated certainty.
        top_linking = EntityLinking.query.filter(EntityLinking.entity_id == entity.id) \
            .order_by(EntityLinking.updated_certainty.desc()).first()

        if top_linking and top_linking.updated_certainty > NED_CUTOFF_THRESHOLD:
            if top_linking.linkable_type == 'Party':
                if not top_linking.linkable_object.as_dict() in parties:
                    parties.append(top_linking.linkable_object.as_dict())
            elif top_linking.linkable_type == 'Politician':
                if not top_linking.linkable_object.as_dict() in politicians:
                    politicians.append(top_linking.linkable_object.as_dict())

    return {
        'article_id': article.id,
        'parties': parties,
        'politicians': politicians
    }
