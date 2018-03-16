from app.modules.common.utils import string_similarity
from whoswho import who
from gender_guesser import detector
import logging

gender_detector = detector.Detector()
logger = logging.getLogger('disambiguation_features')


def f_name_similarity(mention, candidate):
    last_names = candidate.last_name_array
    score = 0

    for last_name in last_names:
        sim_last = string_similarity(last_name, mention)
        sim_first = string_similarity((candidate.first_name + ' ' + last_name), mention)
        sim_full = string_similarity(candidate.full_name, mention)
        score =  max(sim_first, sim_last, sim_full)

    return score


def f_who_name_similarity(mention, candidate):
    sim_first = who.ratio(mention, (candidate.first_name + ' ' + candidate.last_name)) / 100
    sim_initials = who.ratio(mention, candidate.full_name) / 100
    return max(sim_first, sim_initials)


def f_first_name_similarity(mention, candidate):
    mention_names = mention.lower().split(' ')
    candidate_first_names = candidate.first_name.lower().split(' ')

    sim = 0
    for name in mention_names:
        if name in candidate_first_names:
            sim = 1
    return sim

def f_initials_similarity(mention, candidate):
    first_letter_mention = mention[0].lower()
    first_letter_candidate = candidate.initials[0].lower()

    if first_letter_mention == first_letter_candidate:
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
    candidate_parties = candidate.party.lower().split('/')
    sim = 0
    if len(document['parties']) > 0:
        document_parties = [x.lower() for x in document['parties']]
        for candidate_party in candidate_parties:
            if candidate_party in document_parties:
                sim = 1.0
    return sim


def f_location_similarity(document, candidate):
    if document['location'].lower() == candidate.municipality.lower():
        return 1.0
    else:
        return 0.0


def f_gender_similarity(mention, candidate):
    mention_first_name = mention.split(' ')[0]
    mention_gender = gender_detector.get_gender(mention_first_name)
    candidate_gender = candidate.gender

    if mention_gender == 'unknown' or candidate_gender == 'unknown':
        return 0
    elif mention_gender == 'andy':
        return 0.15
    elif candidate_gender == 'female' and (mention_gender == 'female' or mention_gender == 'mostly_female'):
        return 1.0
    elif candidate_gender == 'male' and (mention_gender == 'male' or mention_gender == 'mostly_male'):
        return 1.0
    else:
        return 0


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