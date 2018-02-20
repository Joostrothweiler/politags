import logging

import nl_core_news_sm
from sqlalchemy import func

from app.models.models import *
from app.modules.common.crud import update_entity_count
from app.modules.common.utils import pure_len
from app.modules.enrichment.named_entities.nlp_model.pipelines import PoliticianRecognizer, PartyRecognizer

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
        doc_ent_text = doc_ent.text.strip()
        # Check if the entity is already in the database.
        entity = Entity.query.filter(Entity.article_id == article.id) \
            .filter(Entity.text == doc_ent_text) \
            .filter(Entity.label == doc_ent.label_).first()

        if entity:
            entity.count += 1
        elif entity_text_has_valid_length(doc_ent):
            # Create the entity in the database.
            entity = Entity(text=doc_ent_text,
                            label=doc_ent.label_,
                            start_pos=doc_ent.start_char,
                            end_pos=doc_ent.end_char)
            entity.article = article
            db.session.add(entity)

    return article.entities


def entity_text_has_valid_length(entity) -> bool:
    """
    Check whether the entity has a valid entity.text length such that we can insert it in the database.
    :param entity: NLP entity processed by Spacy.
    :return: Boolean whether entity has valid text length.
    """
    if entity and entity.text:
        return pure_len(entity.text) > 1 and len(entity.text) < 50
    return False
