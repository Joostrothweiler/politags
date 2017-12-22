import json
import numpy as np
from sqlalchemy import or_, func

from app import db
from app.models.models import Politician, Party, EntityLinking
from app.modules.common.utils import string_similarity, parse_human_name
from app.modules.entities.disambiguation_features import f_context_similarity, f_name_similarity, \
    f_first_name_similarity, f_party_similarity
from app.modules.entities.nlp_model.tooling.disambiguation_tooling import write_classifier_training_file, \
    candidate_present_in_document
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
        f_name = f_name_similarity(entity.text, candidate)
        f_first_name = f_first_name_similarity(entity.text, candidate)
        f_party = f_party_similarity(document, candidate)
        f_context = f_context_similarity(document, entities, candidate)

        write_classifier_training_file(document, [f_name, f_first_name, f_party, f_context], candidate)

        if candidate_present_in_document(document, candidate):
            print(
                'This is the actual candidate! feature vector: [{},{},{},{}]. {}'.format(f_name, f_first_name, f_party,
                                                                                         f_context,
                                                                                         candidate.full_name))

        weighted_sim = weighted_similarity_score(f_name, f_context)

        if weighted_sim > NED_CUTOFF_THRESHOLD:
            store_entity_politician_linking(entity, candidate, weighted_sim)


def get_candidate_politicians(mention):
    human_name = parse_human_name(mention)
    candidates = Politician.query.filter(
        or_(func.lower(Politician.last_name) == func.lower(human_name['first_name']),
            func.lower(Politician.last_name) == func.lower(human_name['last_name']))).all()
    candidate_count = Politician.query.filter(
        or_(func.lower(Politician.last_name) == func.lower(human_name['first_name']),
            func.lower(Politician.last_name) == func.lower(human_name['last_name']))).count()
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
