import numpy as np
from sqlalchemy import or_, func

from app import db
from app.models.models import Politician, Party, EntitiesPoliticians, EntitiesParties
from app.modules.common.utils import string_similarity, collection_as_dict


def named_entity_disambiguation(document, entities):
    for e in entities:
        if e.label == 'PER':
            politician_disambiguation(document, entities, e)

        if e.label == 'ORG':
            party_disambiguation(document, entities, e)


def politician_disambiguation(document, entities, entity):
    # Get candidates
    candidates = get_candidate_politicians(entity.text)
    if candidates:
        # For each candidate, compute mention_name_similarity
        name_sim = politician_mention_name_similarity(entity.text, candidates)
        # For each candidate, compute context_similarity
        context_sim = politician_context_similarity(entity.text, document, entities, candidates)
        # Return the average of the two
        scored_candidates = average_sim(candidates, name_sim, context_sim)
        politician, certainty = politician_optimal_candidate(scored_candidates)
        # Store in database
        store_entity_politician_linking(entity, politician, certainty)
    else:
        print('No candidates found for {}'.format(entity.text))


def politician_context_similarity(mention, document, entities, candidates):
    result = {}
    # Fill document entries for comparison
    document_entries = []
    for entity in entities:
        document_entries.append(entity.text)
    for party in document['parties']:
        document_entries.append(party)
    document_entries.append(document['collection'])
    document_entries.append(document['location'])
    document_string = ' '.join(document_entries)

    for candidate_politician in candidates:
        # Fill candidate data for comparison
        candidate_politician_string = ' '.join([candidate_politician.first_name,
                                                candidate_politician.last_name,
                                                candidate_politician.party,
                                                candidate_politician.role,
                                                candidate_politician.municipality])

        result[candidate_politician.id] = string_similarity(document_string, candidate_politician_string)
    return result


def politician_mention_name_similarity(mention, candidates):
    result = {}
    for candidate_politician in candidates:
        result[candidate_politician.id] = string_similarity(candidate_politician.last_name, mention)

    return result


# TODO: Improve method to return a maximum number of candidates
def get_candidate_politicians(mention):
    mention_arr = mention.split(' ')
    # Get based on last name match
    candidates = Politician.query.filter(or_(*[Politician.last_name.like(name) for name in mention_arr])).all()
    return candidates


def average_sim(candidates, name_sim, context_sim):
    result = []
    for candidate in candidates:
        # TODO: We could improve the weight distribution based on the level of ambiguity stored in the database.
        # High ambiguity -> focus on context, low ambiguity, focus on name.
        result.append({
            'id': candidate.id,
            'score': 0.9 * name_sim[candidate.id] + 0.1 * context_sim[candidate.id]
        })
    return result


def politician_optimal_candidate(scored_candidates):
    max = 0
    max_id = None

    for candidate in scored_candidates:
        if candidate['score'] > max:
            max = candidate['score']
            max_id = candidate['id']

    return Politician.query.filter(Politician.id == max_id).first(), max


def store_entity_politician_linking(entity, politician, certainty):
    # print('Linking {} to {}'.format(entity.text, (politician.full_name)))
    a = EntitiesPoliticians(certainty=certainty)
    a.politician = politician
    entity.politicians.append(a)
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
    else:
        print('No candidate parties found for {}'.format(entity.text))


def store_entity_party_linking(entity, party, certainty):
    # print('Linking {} to {}'.format(entity.text, party.abbreviation))
    a = EntitiesParties(certainty=certainty)
    a.party = party
    entity.parties.append(a)
    db.session.add(entity)
