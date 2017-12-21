import numpy as np
from sqlalchemy import or_, func

from app import db
from app.models.models import Politician, Party, EntityLinking
from app.modules.common.utils import string_similarity, parse_human_name
from app.settings import NED_CUTOFF_THRESHOLD, NED_STRING_SIM_WEIGHT, NED_CONTEXT_SIM_WEIGHT


def named_entity_disambiguation(document, entities):
    for entity in entities:
        if entity.label == 'PER':
            politician_disambiguation(document, entities, entity)

        if entity.label == 'ORG':
            party_disambiguation(document, entities, entity)


def politician_disambiguation(document, entities, entity):
    candidates = get_candidate_politicians(entity.text)

    for candidate in candidates:
        name_sim = politician_mention_name_similarity(entity.text, candidate)
        context_sim = politician_context_similarity(document, entities, candidate)
        weighted_sim = weighted_similarity_score(name_sim, context_sim)

        if weighted_sim > NED_CUTOFF_THRESHOLD:
            store_entity_politician_linking(entity, candidate, weighted_sim)


def politician_context_similarity(document, entities, candidate):
    # Fill document entries for comparison
    document_entries = []
    for entity in entities:
        document_entries.append(entity.text)
    for party in document['parties']:
        document_entries.append(party)
    document_entries.append(document['collection'])
    document_entries.append(document['location'])

    candidate_array = [candidate.title,
                       candidate.first_name,
                       candidate.last_name,
                       candidate.party,
                       candidate.role,
                       candidate.municipality]

    sim = jaccard_distance(document_entries, candidate_array)
    print('Similarity between "{}" and {} is {}'.format(document['parties'], candidate.full_name, sim))
    return sim


def jaccard_distance(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    print(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection / union)


def politician_mention_name_similarity(mention, candidate):
    sim = string_similarity(candidate.last_name, mention)
    # print('Similarity between "{}" and {} is {}'.format(mention, candidate.full_name, sim))
    return sim


def get_candidate_politicians(mention):
    human_name = parse_human_name(mention)
    candidates = Politician.query.filter(
        or_(Politician.last_name == human_name['first_name'], Politician.last_name == human_name['last_name'])).all()
    candidate_count = Politician.query.filter(
        or_(Politician.last_name == human_name['first_name'], Politician.last_name == human_name['last_name'])).count()
    print('Human Name: {}, #candidates: {}'.format(human_name, candidate_count))
    return candidates


def weighted_similarity_score(name_sim, context_sim):
    return NED_STRING_SIM_WEIGHT * name_sim + NED_CONTEXT_SIM_WEIGHT * context_sim


def store_entity_politician_linking(entity, politician, certainty):
    a = EntityLinking(certainty=certainty)
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


def store_entity_party_linking(entity, party, certainty):
    linking = EntityLinking(certainty=certainty)
    linking.linkable_object = party
    entity.linkings.append(linking)
    db.session.add(entity)
