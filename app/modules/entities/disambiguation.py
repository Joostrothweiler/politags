import numpy as np
from sqlalchemy import or_, func

from app import db
from app.models.models import Politician, Party, EntityLinking
from app.modules.entities.disambiguation_features import *
from app.modules.entities.nlp_model.tooling.disambiguation_tooling import candidate_present_in_document


def named_entity_disambiguation(document, entities):
    for entity in entities:
        if entity.label == 'PER':
            politician_disambiguation(document, entities, entity)

        if entity.label == 'ORG':
            party_disambiguation(document, entities, entity)


def politician_disambiguation(document, entities, entity):
    candidates = get_candidate_politicians(entity.text)
    result = []

    for candidate in candidates:
        f_name = f_name_similarity(entity.text, candidate)
        f_first_name = f_first_name_similarity(entity.text, candidate)
        f_who_name = f_who_name_similarity(entity.text, candidate)
        f_role = f_role_in_document(document, candidate)
        f_party = 30*f_party_similarity(document, candidate)
        f_context = 30*f_context_similarity(document, entities, candidate)
        feature_vector = [f_name, f_first_name, f_who_name, f_role, f_party, f_context]

        result.append({'candidate' : candidate, 'score': np.sum(feature_vector) })

    while len(result) > 2:
        min_score  = float('inf')
        min_obj = None
        for obj in result:
            if obj['score'] < min_score :
                min_score = obj['score']
                min_obj = obj

        result.remove(min_obj)

    for obj in result:
        candidate = obj['candidate']
        # print("Linked {} to {} with prob {}".format(entity.text, candidate.full_name, f_who_name_similarity(entity.text, candidate)))
        store_entity_politician_linking(entity, candidate, f_who_name_similarity(entity.text, candidate))


def get_candidate_politicians(mention):
    # Remove starting and trailing whitespace from string.
    mention_stripped = mention.strip()
    # Possible mentions: Jeroen, J. van der Maat, Jeroen van der Maat, van der Maat
    # Match on last name in database: van der Maat
    name = mention_stripped
    name_array = mention_stripped.split(' ')
    candidates = []

    while len(candidates) == 0 and len(name_array) > 0:
        name = ' '.join(name_array)
        candidates = Politician.query.filter(
            or_(func.lower(Politician.last_name) == func.lower(name),
                func.lower(Politician.last_name) == func.lower(name))).all()
        name_array.pop(0)

    # If no candidates found based on exact matches so far.
    # Next call decreases Precision but increases Recall
    if len(candidates) == 0:
        candidates = Politician.query.filter(
            or_(func.lower(Politician.last_name).contains(func.lower(name)),
                func.lower(Politician.last_name).contains(func.lower(name)))).all()

    # For evaluation - print some info
    # print('Mention: {}, #candidates: {}'.format(mention, len(candidates)))
    # print([x.full_name for x in candidates])

    return candidates


def store_entity_politician_linking(entity, politician, initial_certainty):
    a = EntityLinking(initial_certainty=initial_certainty)
    a.linkable_object = politician
    entity.linkings.append(a)
    db.session.add(entity)


#########
# PARTIES
#########
def party_disambiguation(document, entities, entity):
    candidates = Party.query.filter(or_(func.lower(Party.abbreviation) == func.lower(entity.text),
                                        func.lower(Party.name) == func.lower(entity.text))).all()

    if len(candidates) > 0:
        max_sim = 0
        max_party = None

        for candidate_party in candidates:
            candidate_sim = np.maximum(string_similarity(candidate_party.abbreviation, entity.text),
                                       string_similarity(candidate_party.name, entity.text))
            if candidate_sim > max_sim:
                max_sim = candidate_sim
                max_party = candidate_party

        store_entity_party_linking(entity, max_party, max_sim)


def store_entity_party_linking(entity, party, initial_certainty):
    linking = EntityLinking(initial_certainty=initial_certainty)
    linking.linkable_object = party
    entity.linkings.append(linking)
    db.session.add(entity)
