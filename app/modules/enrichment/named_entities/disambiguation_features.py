from app.modules.common.utils import string_similarity
from whoswho import who


def f_name_similarity(mention, candidate):
    sim_last = string_similarity(candidate.last_name, mention)
    sim_given = string_similarity((candidate.given_name + ' ' + candidate.last_name), mention)
    sim_first = string_similarity((candidate.first_name + ' ' + candidate.last_name), mention)
    sim_full = string_similarity(candidate.full_name, mention)
    return max(sim_first, sim_last, sim_given, sim_full)


def f_who_name_similarity(mention, candidate):
    sim_given = who.ratio(mention, (candidate.given_name + ' ' + candidate.last_name)) / 100
    sim_first = who.ratio(mention, (candidate.first_name + ' ' + candidate.last_name)) / 100
    sim_initials = who.ratio(mention, candidate.full_name) / 100
    return max(sim_given, sim_first, sim_initials)


def f_first_name_similarity(mention, candidate):
    sim = 0
    if len(candidate.first_name) > 1 and mention.split(' ')[0].lower() == candidate.first_name.lower():
        sim = 1
    if len(candidate.given_name) > 1 and mention.split(' ')[0].lower() == candidate.given_name.lower():
        sim = 1
    return sim


def f_initials_similarity(mention, candidate):
    parts_of_mention_name = mention[0].lower()
    first_letter_candidate = candidate.initials.split('.')[0].lower()

    if parts_of_mention_name[0] == first_letter_candidate:
        return 1
    else:
        return 0


def f_role_in_document(document, candidate):
    role_splitted = candidate.role.lower().split(' ')
    sim = 0

    if len(role_splitted) > 0:
        for role in role_splitted:
            if role in document['text_description'].lower():
                sim = 1
    else:
        sim = 0
    return sim


def f_party_similarity(document, candidate):
    if len(document['parties']) > 0:
        parties = [x.lower() for x in document['parties']]
        if candidate.party.lower() in parties:
            return 1.0
        else:
            return 0.0
    else:
        return 0.0


def f_location_similarity(document, candidate):
    if document['location'].lower() == candidate.municipality.lower():
        return 1.0
    else:
        return 0.0


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
