import numpy as np
from sqlalchemy import or_, func

from app import db
from app.models.models import Politician, Party, EntityLinking, Entity, Article
from app.modules.entities.disambiguation_features import *


def named_entity_disambiguation(entities: list, document: dict):
    """
    Process entities found in a document using Spacy and store any linkings found.
    :param entities: entities found in document.
    :param document: simple doc from API.
    """
    for entity in entities:
        if entity.label == 'PER':
            politician_disambiguation(document, entities, entity)

        if entity.label == 'ORG':
            party_disambiguation(document, entities, entity)
    # Here we may want to call post_process_disambiguation_linkings...


def politician_disambiguation(document: dict, doc_entities: list, entity: Entity):
    """
    Compute and store the most probable linkings for politicians in the database.
    :param document: simple doc from poliflow.
    :param doc_entities: The entities found in the document using Spacy NER.
    :param entity: The entity from the database we are currently evaluating.
    """
    MAX_NUMBER_OF_LINKINGS = 2
    F_ROLE_WEIGHT = 30
    F_PARTY_WEIGHT = 30
    FLOAT_INF = float('inf')

    candidates = get_candidate_politicians(entity)
    result = []

    for candidate in candidates:
        f_name = f_name_similarity(entity.text, candidate)
        f_first_name = f_first_name_similarity(entity.text, candidate)
        f_who_name = f_who_name_similarity(entity.text, candidate)
        f_role = f_role_in_document(document, candidate)
        f_party = F_ROLE_WEIGHT * f_party_similarity(document, candidate)
        f_context = F_PARTY_WEIGHT * f_context_similarity(document, doc_entities, candidate)
        feature_vector = [f_name, f_first_name, f_who_name, f_role, f_party, f_context]
        # TODO: Normalize this count so that we can use it directly as certainty instead of name similarity.
        result.append({'candidate': candidate, 'score': np.sum(feature_vector)})

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
        store_entity_politician_linking(entity, candidate, f_who_name_similarity(entity.text, candidate))


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
        candidates = Politician.query.filter(
            or_(func.lower(Politician.last_name) == func.lower(name),
                func.lower(Politician.last_name) == func.lower(name))).all()
        name_array.pop(0)

    # If no candidates found based on exact matches so far, take LAST PART OF NAME and look for this one.
    if len(candidates) == 0:
        candidates = Politician.query.filter(
            or_(func.lower(Politician.last_name).contains(func.lower(name)),
                func.lower(Politician.last_name).contains(func.lower(name)))).all()

    return candidates


def store_entity_politician_linking(entity: Entity, politician: Politician, initial_certainty: float):
    """
    Store a linking between a database entity and a politician with a given certainty.
    :param entity: Entity from the database.
    :param politician: Candidate politician from the database.
    :param initial_certainty: Intial certainty score computed based on similarity features and weights.
    """
    a = EntityLinking(initial_certainty=initial_certainty)
    a.linkable_object = politician
    entity.linkings.append(a)
    db.session.add(entity)


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

        store_entity_party_linking(entity, max_party, max_sim)


def store_entity_party_linking(entity: Entity, party: Party, initial_certainty: float):
    """
    Store the linkings between an entity and a party in the database.
    :param entity: Entity in the database.
    :param party: Party in the database.
    :param initial_certainty: Intial certainty score computed based on similarity features and weights.
    """
    linking = EntityLinking(initial_certainty=initial_certainty)
    linking.linkable_object = party
    entity.linkings.append(linking)
    db.session.add(entity)


# FIXME: Does not add any gain in recall/precision like this with the current setup. Therefore, leave out for now.
def post_process_disambiguation_linkings(entities: list):
    entity_ids = [e.id for e in entities]
    entity_linkings = EntityLinking.query.filter(EntityLinking.entity_id.in_(entity_ids)).order_by(
        EntityLinking.initial_certainty.desc()).all()

    for high_certainty_linking in entity_linkings:
        for low_certainty_linking in entity_linkings:
            if not high_certainty_linking == low_certainty_linking and \
                    high_certainty_linking.linkable_object == low_certainty_linking.linkable_object:
                # Remove all linkings on the lower quality entity
                low_quality_entity = low_certainty_linking.entity
                EntityLinking.query.filter(EntityLinking.entity == low_quality_entity).delete()
