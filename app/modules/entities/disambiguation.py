import numpy as np
from sqlalchemy import or_, func

from app import db
from app.models.models import Politician, Party, EntitiesPoliticians, EntitiesParties
from app.modules.common.utils import string_similarity, collection_as_dict


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
        result = politician_optimal_candidate(scored_candidates)

        print(entity.text)
        print(result.as_dict())
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
                                                candidate_politician.city])

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
    match = Politician.query.filter(or_(*[Politician.last_name.like(name) for name in mention_arr]))
    # Get based on first letter match on first name
    first_letter = mention_arr[0][0]
    letter_match = Politician.query.filter(Politician.first_name.contains(first_letter))
    # Return the union of the two.
    candidates = match.union(letter_match)
    return candidates


def average_sim(candidates, name_sim, context_sim):
    result = []
    for candidate in candidates:
        # TODO: We could improve the weight distribution based on the level of ambiguity stored in the database.
        # High ambiguity -> focus on context, low ambiguity, focus on name.
        result.append({
            'id': candidate.id,
            'score': 0.7 * name_sim[candidate.id] + 0.3 * context_sim[candidate.id]
        })
    return result


def politician_optimal_candidate(scored_candidates):
    max = 0
    max_id = None

    for candidate in scored_candidates:
        if candidate['score'] > max:
            max = candidate['score']
            max_id = candidate['id']

    return Politician.query.filter(Politician.id == max_id).first()

#########
# PARTIES
#########
def party_disambiguation(document, entities, entity):
    candidate_parties = party_mention_name_similarity(entity.text, 1)
    # print(entity.text)
    # print(collection_as_dict(candidate_parties))


def party_mention_name_similarity(mention, k):
    candidate_parties = Party.query.all()
    candidates = [{'id': 0, 'sim': 0}] * k
    min_sim = 0

    for candidate_party in candidate_parties:
        sim1 = string_similarity(candidate_party.name, mention)
        sim2 = string_similarity(candidate_party.abbreviation, mention)
        sim = np.maximum(sim1, sim2)

        if sim == 1.0:
            return [candidate_party]
        if sim > min_sim:
            remove_can = next((item for item in candidates if item['sim'] == min_sim))
            candidates.remove(remove_can)
            candidates.append({'id': candidate_party.id, 'sim': sim})

            min_sim = 1
            for item in candidates:
                if item['sim'] < min_sim:
                    min_sim = item['sim']

    result = []
    for item in candidates:
        result.append(Party.query.filter(Party.id == item['id']).first())
    return result





