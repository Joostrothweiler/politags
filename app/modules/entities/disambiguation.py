import numpy as np
import pickle
from sklearn.linear_model import Perceptron
from sqlalchemy import or_, func

from app import db
from app.models.models import Politician, Party, EntityLinking
from app.modules.entities.disambiguation_features import *
from app.modules.entities.nlp_model.tooling.disambiguation_tooling import write_classifier_training_file
from app.settings import NED_CUTOFF_THRESHOLD

disambiguation_model = pickle.load(open('app/modules/entities/nlp_model/disambiguation_model.sav', 'rb'))

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
        f_who_name = f_who_name_similarity(entity.text, candidate)
        f_party = f_party_similarity(document, candidate)
        f_context = f_context_similarity(document, entities, candidate)
        feature_vector = [f_name, f_first_name, f_who_name, f_party, f_context]
        # Write to file for training
        write_classifier_training_file(document, feature_vector, candidate)
        # Classify
        prediction_prob = classifier_probability(feature_vector)

        if prediction_prob > NED_CUTOFF_THRESHOLD:
            print("Linked {} to {} with prob {}".format(entity.text, candidate.full_name, prediction_prob))
            store_entity_politician_linking(entity, candidate, prediction_prob)


def get_candidate_politicians(mention):
    # Remove starting and trailing whitespace from string.
    mention = mention.strip()
    # Possible mentions: Jeroen, J. van der Maat, Jeroen van der Maat, van der Maat
    # Match on last name in database: van der Maat
    name = mention
    mention_array = mention.split(' ')
    candidate_count = 0

    # FIXME: This method assumes that there are no weird strings at the end of the mention string (this would fail).
    while candidate_count == 0 and len(mention_array) > 0:
        name = ' '.join(mention_array)
        candidate_count = Politician.query.filter(
            or_(func.lower(Politician.last_name) == func.lower(name),
                func.lower(Politician.last_name) == func.lower(name))).count()

        mention_array.pop(0)

    candidates = Politician.query.filter(
        or_(func.lower(Politician.last_name) == func.lower(name),
            func.lower(Politician.last_name) == func.lower(name))).all()

    # For evaluation - print some info
    print('Mention: {}, #candidates: {}'.format(mention, candidate_count))
    for c in candidates:
        print(c.full_name)

    return candidates


def classifier_probability(feature_vector):
    # Classifier returns a certainty
    # We return the probability for true
    candidate_confidence = disambiguation_model.predict_proba([feature_vector])
    print(candidate_confidence)
    print(disambiguation_model.predict([feature_vector]))
    return candidate_confidence[0][1]


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
