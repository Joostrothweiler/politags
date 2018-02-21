import logging

import nl_core_news_sm
from sqlalchemy import func

from app.models.models import Politician, Entity, Article
from app.modules.enrichment.named_entities.crud import update_entity_count, create_entity_or_increment_count
from app.modules.enrichment.named_entities.spacy.pipelines import PoliticianRecognizer, PartyRecognizer

logger = logging.getLogger('recognition')


def init_nlp():
    """
    Initialize the NLP module with PhraseMatcher
    """
    logger.info('NLP Module : Initializing')
    global nlp
    politicians = []
    parties = []
    for politician in Politician.query.filter(func.length(Politician.given_name) > 1).all():
        politicians.append(politician.given_name + ' ' + politician.last_name)

    nlp = nl_core_news_sm.load()
    politician_pipe = PoliticianRecognizer(nlp, politicians)
    party_pipe = PartyRecognizer(nlp, parties)
    nlp.add_pipe(politician_pipe, last=True)
    nlp.add_pipe(party_pipe, last=True)
    nlp.remove_pipe('tagger')
    nlp.remove_pipe('parser')
    logger.info('NLP Module : Initialized. Pipelines in use: {}'.format(nlp.pipe_names))


def transform_text_description_to_nlp_doc(document):
    if nlp == None:
        init_nlp()
    return nlp(document['text_description'])


def recognize_named_entities(article: Article, document: dict) -> list:
    """
    Perform Named Entity Recognition on the article in the database, including all types such as LOC, MISC
    :param article: article in the database
    :param nlp_doc: NLP processed document
    :return: database entities for this article.
    """
    # Reset counts to 0 so that we can process the document again and dont have to delete entities.
    article_entities = Entity.query.filter(Entity.article_id == article.id).all()
    for entity in article_entities:
        update_entity_count(entity, 0)

    nlp_doc = transform_text_description_to_nlp_doc(document)
    # Count again.
    for doc_ent in nlp_doc.ents:
        # Strip the entity text so that we have no empty space at the ends.
        create_entity_or_increment_count(article, doc_ent.text, doc_ent.label_, doc_ent.start_char, doc_ent.end_char)

    return article.entities
