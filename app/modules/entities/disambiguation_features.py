from app.modules.common.utils import string_similarity


def f_name_similarity(mention, candidate):
    sim = string_similarity(candidate.last_name, mention)
    # print('Similarity between "{}" and {} is {}'.format(mention, candidate.full_name, sim))
    return sim


def f_first_name_similarity(mention, candidate):
    parts_of_mention_name = mention.split(' ')
    first_letters_candidate = candidate.first_name.split('.')
    sim = 0

    for part_of_name in parts_of_mention_name:
        for first_letter in first_letters_candidate:
            if len(part_of_name) > 0 and part_of_name[0] == first_letter:
                sim = 1
    return sim


def f_party_similarity(document, candidate):
    document_parties = []
    for party in document['parties']:
        document_parties.append(party)
    # TODO this is not a very string way to compare this.
    sim = string_similarity(candidate.party, document['collection'])
    return sim

def f_context_similarity(document, entities, candidate):
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

    [x.lower() for x in document_entries]
    [x.lower() for x in candidate_array]
    sim = jaccard_distance(document_entries, candidate_array)
    # print('Similarity between "{}" and {} is {}'.format(document['parties'], candidate.full_name, sim))
    return sim



def jaccard_distance(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection / union)


