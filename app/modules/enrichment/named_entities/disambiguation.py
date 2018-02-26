import logging
import numpy as np
from sqlalchemy import or_, func

from app import db
from app.models.models import Politician, Party, EntityLinking, Entity, Article
from app.modules.enrichment.named_entities.disambiguation_features import *

logger = logging.getLogger('disambiguation')


# with open('app/modules/entities/nlp_model/test_tree_clf.pkl', 'rb') as fid:
#     classifier = pickle.load(fid)


def named_entity_disambiguation(article : Article, document: dict):
    """
    Process entities found in a document using Spacy and store any linkings found.
    :param entities: entities found in document.
    :param document: simple doc from API.
    """
    entities = article.entities

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
    MAX_NUMBER_OF_LINKINGS = 2
    FLOAT_INF = float('inf')

    candidates = get_candidate_politicians(entity)
    result = []

    for candidate in candidates:
        candidate_fv = compute_politician_feature_vector(document, doc_entities, entity, candidate)
        candidate_fv[1] = 30 * candidate_fv[1]
        candidate_fv[2] = 100 * candidate_fv[2]
        candidate_fv[4] = 50 * candidate_fv[4]
        candidate_fv[6] = 50 * candidate_fv[6]

        result_object = {'candidate': candidate, 'feature_vector': candidate_fv, 'score': np.sum(candidate_fv)}
        result.append(result_object)

    while len(result) > MAX_NUMBER_OF_LINKINGS:
        min_score = FLOAT_INF
        min_obj = None
        for obj in result:
            if obj['score'] < min_score:
                min_score = obj['score']
                min_obj = obj

        result.remove(min_obj)

    for obj in result:
        candidate = obj['candidate']
        candidate_fv = obj['feature_vector']
        store_entity_linking(entity, candidate, compute_politician_certainty(candidate_fv))


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

    return [f_name, f_initials, f_first_name, f_who_name, f_location, f_role, f_party, f_context]


def compute_politician_certainty(candidate_feature_vector: list) -> float:
    """
    Compute the certainty of a linking based on the feature vector.
    :param candidate_feature_vector: A feature vector representing the relation between a entity, document and linking.
    :return: Certainty (float).
    """
    # TODO: Compute an actual certainty measure here instead of writing f_who_name. Should be result of active learning classifier.
    return min(candidate_feature_vector[3], 0.95)


def get_candidate_politicians(entity: Entity) -> list:
    """
    Get all candidate politicians for this entity.
    :param entity: entity from the database.
    :return: candidates for linkings.
    """
    # Possible entity_texts: Jeroen, J. van der Maat, Jeroen van der Maat, van der Maat
    # Match on last name in database: van der Maat
    name = entity.text
    name_array = entity.text.split(' ')
    candidates = []

    while len(candidates) == 0 and len(name_array) > 0:
        name = ' '.join(name_array)
        candidates = Politician.query.filter(func.lower(Politician.last_name) == func.lower(name)).all()
        name_array.pop(0)

    # If no candidates found based on exact matches so far, take LAST PART OF NAME and look for this one.
    # if len(candidates) == 0:
    #     candidates = Politician.query.filter(
    #         or_(func.lower(Politician.last_name).contains(func.lower(name)),
    #             func.lower(Politician.last_name).contains(func.lower(name)))).all()

    return candidates


def party_disambiguation(document: dict, entities: list, entity: Entity):
    """
    Generate candidates based on entity and store linkings if found.
    :param document: Simple doc from API.
    :param entities: Collection of entities from doc.
    :param entity: Entity in db.
    """
    ZERO = 0
    candidates = Party.query.filter(or_(func.lower(Party.abbreviation) == func.lower(entity.text),
                                        func.lower(Party.name) == func.lower(entity.text))).all()

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