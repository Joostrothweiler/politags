from app.modules.common.utils import string_similarity
from whoswho import who


def f_name_similarity(mention, candidate):
    sim = string_similarity(candidate.last_name, mention)
    return sim


def f_first_name_similarity(mention, candidate):
    parts_of_mention_name = mention.split(' ')
    first_letter_candidate = candidate.first_name.split('.')[0]
    sim = 0.0

    for part_of_name in parts_of_mention_name:
        if len(part_of_name) > 0 and part_of_name[0] == first_letter_candidate:
            sim = 1.0
    return sim

def f_role_in_document(document, candidate):
    if candidate.role.lower() in document['text_description'].lower():
        return 1.0
    else:
        return 0.0


def f_who_name_similarity(mention, candidate):
    sim = who.ratio(mention, candidate.full_name) / 100
    return sim


def f_party_similarity(document, candidate):
    if len(document['parties']) > 0:
        parties = [x.lower() for x in document['parties']]
        if candidate.party.lower() in parties:
            return 1.0
        else:
            return 0.0
    else:
        return 0.5


def f_context_similarity(document, entities, candidate):
    # Fill document entries for comparison
    document_entries = []
    for entity in entities:
        document_entries.append(entity.text)
    for party in document['parties']:
        document_entries.append(party)
    document_entries.append(document['collection'])
    document_entries.append(document['location'])

    candidate_array = [candidate.last_name,
                       candidate.party,
                       candidate.municipality.split(' ')[-1]]

    a = [x.lower() for x in document_entries]
    b = [x.lower() for x in candidate_array]

    sim = jaccard_distance(a, b)
    return sim


def jaccard_distance(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection / union)


