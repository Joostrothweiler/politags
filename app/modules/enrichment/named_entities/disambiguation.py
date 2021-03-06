import logging
import pickle
import numpy as np
from sqlalchemy import or_, func, and_

from app import db
from app.models.models import Politician, Party, EntityLinking, Entity, Article
from app.modules.enrichment.named_entities.disambiguation_features import *

logger = logging.getLogger('disambiguation')
ned_classifier = None


def init_ned_classifier():
    global ned_classifier
    ned_classifier = pickle.load(open('app/modules/enrichment/named_entities/disambiguation_clf.sav', 'rb'))
    logger.info('NED classifier loaded from disk.')


def named_entity_disambiguation(article: Article, document: dict):
    """
    Process entities found in a document using Spacy and store any linkings found.
    :param entities: entities found in document.
    :param document: simple doc from API.
    """
    entities = Entity.query.filter(Entity.article_id == article.id).filter(func.length(Entity.text) > 1).all()

    for entity in entities:
        if entity.label == 'PER':
            politician_disambiguation(document, entities, entity)

        if entity.label == 'ORG':
            party_disambiguation(document, entities, entity)


def politician_disambiguation(document: dict, doc_entities: list, entity: Entity):
    """
    Compute and store the most probable linkings for politicians in the database.
    :param document: simple doc from poliflow.
    :param doc_entities: The entities found in the document using Spacy NER.
    :param entity: The entity from the database we are currently evaluating.
    """
    if ned_classifier == None:
        init_ned_classifier()

    MAX_NUMBER_OF_LINKINGS = 2
    FLOAT_INF = float('inf')

    candidates = get_candidate_politicians(entity)
    result = []

    for candidate in candidates:
        candidate_fv = compute_politician_feature_vector(document, doc_entities, entity, candidate)
        certainty = compute_politician_certainty(candidate_fv)

        result_object = {'candidate': candidate, 'certainty': certainty}
        result.append(result_object)

    while len(result) > MAX_NUMBER_OF_LINKINGS:
        min_score = FLOAT_INF
        min_obj = None
        for obj in result:
            if obj['certainty'] < min_score:
                min_score = obj['certainty']
                min_obj = obj

        result.remove(min_obj)

    for obj in result:
        store_entity_linking(entity, obj['candidate'], obj['certainty'])


def compute_politician_feature_vector(document: dict, doc_entities: list, entity: Entity, candidate: Politician):
    """
    Compute a feature vector that represents the relationship between an entity and a candidate politician.
    :param document:
    :param doc_entities:
    :param entity:
    :param candidate:
    :return:
    """
    f_name = f_name_similarity(entity.text, candidate)
    f_initials = f_initials_similarity(entity.text, candidate)
    f_first_name = f_first_name_similarity(entity.text, candidate)
    f_who_name = f_who_name_similarity(entity.text, candidate)
    f_location = f_location_similarity(document, candidate)
    f_role = f_role_in_document(document, candidate)
    f_party = f_party_similarity(document, candidate)
    f_context = f_context_similarity(document, doc_entities, candidate)
    f_gender = f_gender_similarity(entity.text, candidate)

    return [f_name, f_initials, f_first_name, f_who_name, f_location, f_role, f_party, f_context, f_gender]


def compute_politician_certainty(candidate_fv: list) -> float:
    """
    Compute the certainty of a linking based on the feature vector.
    :param candidate_feature_vector: A feature vector representing the relation between a entity, document and linking.
    :return: Certainty (float).
    """
    # Return the maximum probability found by the classifier - this should be the probability found for positive label.
    certainty = ned_classifier.predict_proba([candidate_fv])[0][1]
    return min(certainty, 0.95)


def get_candidate_politicians(entity: Entity) -> list:
    """
    Get all candidate politicians for this entity.
    :param entity: entity from the database.
    :return: candidates for linkings.
    """
    # Possible entity_texts: Jeroen, J. van der Maat, Jeroen van der Maat, van der Maat
    # Match on last name in database: van der Maat
    name_array = entity.text.split(' ')
    candidates = []

    while len(candidates) == 0 and len(name_array) > 0:
        name = ' '.join(name_array)

        candidates = Politician.query.filter(or_(
            Politician.last_name == name,
            and_(
                Politician.last_name.contains('-'),
                Politician.last_name.contains(name)
            )
        )).all()
        name_array.pop(0)

    return candidates


def party_disambiguation(document: dict, entities: list, entity: Entity):
    """
    Generate candidates based on entity and store linkings if found.
    :param document: Simple doc from API.
    :param entities: Collection of entities from doc.
    :param entity: Entity in db.
    """
    ZERO = 0
    candidates = get_candidate_parties(entity)

    if len(candidates) > ZERO:
        max_sim = ZERO
        max_party = None

        for candidate_party in candidates:
            candidate_sim = np.maximum(string_similarity(candidate_party.abbreviation, entity.text),
                                       string_similarity(candidate_party.name, entity.text))
            if candidate_sim > max_sim:
                max_sim = candidate_sim
                max_party = candidate_party

        store_entity_linking(entity, max_party, max_sim)


def get_candidate_parties(entity: Entity):
    conditions = []

    # conditions.append(Party.abbreviation.ilike('%{}%'.format(entity.text)))
    # conditions.append(Party.name.ilike('%{}%'.format(entity.text)))

    candidates = Party.query.all()
    return candidates


def store_entity_linking(entity: Entity, linkable_object: object, initial_certainty: float):
    """
    Store the linkings between an entity and a party in the database.
    :param entity: Entity in the database.
    :param linkable_object: Either party or politician object
    :param initial_certainty: Intial certainty score computed based on similarity features and weights.
    """
    linking = EntityLinking.query.filter(EntityLinking.entity == entity).filter(
        EntityLinking.linkable_object == linkable_object).first()

    if linking:
        linking.initial_certainty = initial_certainty
    else:
        linking = EntityLinking(initial_certainty=initial_certainty)
        linking.linkable_object = linkable_object
        entity.linkings.append(linking)
        db.session.add(entity)
    db.session.commit()
