import logging
import nl_core_news_sm

from sqlalchemy import func

from app import db
from app.models.models import Entity, Article, Politician
from app.modules.common.utils import entity_text_has_valid_length
from app.modules.enrichment.named_entities.spacy.pipelines import PoliticianRecognizer, PartyRecognizer

nlp = None
logger = logging.getLogger('recognition')


def init_nlp():
    """
    Initialize the NLP module with PhraseMatcher
    """
    logger.info('NLP Module : Initializing')
    global nlp
    politicians = []
    parties = []
    # for politician in Politician.query.filter(func.length(Politician.first_name) > 1).all():
    #     politicians.append(politician.first_name + ' ' + politician.last_name)

    nlp = nl_core_news_sm.load()
    politician_pipe = PoliticianRecognizer(nlp, politicians)
    party_pipe = PartyRecognizer(nlp, parties)
    nlp.add_pipe(politician_pipe, last=True)
    nlp.add_pipe(party_pipe, last=True)
    nlp.remove_pipe('tagger')
    nlp.remove_pipe('parser')
    logger.info('NLP Module : Initialized. Pipelines in use: {}'.format(nlp.pipe_names))


def convert_document_description_to_nlp_doc(document):
    # Initialize only if nlp is not yet loaded.
    if nlp == None:
        init_nlp()
    return nlp(document['text_description'])


def named_entity_recognition(article: Article, document: dict) -> list:
    """
    Perform Named Entity Recognition on the article in the database, including all types such as LOC, MISC
    :param article: article in the database
    :param nlp_doc: NLP processed document
    :return: database entities for this article.
    """
    # Reset counts to 0 so that we can process the document again and dont have to delete entities.
    article_entities = Entity.query.filter(Entity.article_id == article.id).all()
    for entity in article_entities:
        entity.count = 0
        db.session.add(entity)

    nlp_doc = convert_document_description_to_nlp_doc(document)

    # Count again.
    for doc_ent in nlp_doc.ents:
        if doc_ent.label_ == 'PER' or doc_ent.label_ == 'ORG':
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

            db.session.commit()
    return article.entities
