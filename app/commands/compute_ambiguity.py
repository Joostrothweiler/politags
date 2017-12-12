import numpy as np

from flask_script import Command

from app import db
from app.models.models import Politician, Party
from app.modules.common.utils import string_similarity


class ComputeAmbiguity(Command):
    """ For parties and politicians, compute an ambiguity score."""

    def run(self):
        compute_politician_ambiguity()


def compute_politician_ambiguity():
    politicians = Politician.query.all()

    for politician in politicians:
        print(politician.id)
        politician.level_of_ambiguity = politician_ambiguity(politician)
        db.session.add(politician)
    db.session.commit()


def politician_ambiguity(politician):
    # Start with 3 categories of ambiguity.
    # 0.25: There is someone with the same last name.
    # 0.50: There is someone with the same last name in the same party
    # 0.75: There is someone with the same last name in the same party and city.
    # +0.1 (max 1.0) for the number of people with same name, party and city.
    ambiguity = 0.0
    same_name = Politician.query.filter(Politician.id!= politician.id)\
        .filter(Politician.last_name == politician.last_name).count()
    if same_name > 0:
        ambiguity = 0.25
    else:
        return ambiguity

    same_name_party = Politician.query.filter(Politician.id!= politician.id) \
        .filter(Politician.party != '') \
        .filter(Politician.last_name == politician.last_name) \
        .filter(Politician.party == politician.party).count()
    if same_name_party > 0:
        ambiguity = 0.50
    else:
        return ambiguity

    same_name_party_city = Politician.query.filter(Politician.id!= politician.id) \
            .filter(Politician.party != '') \
            .filter(Politician.last_name == politician.last_name) \
            .filter(Politician.party == politician.party) \
            .filter(Politician.city == politician.city).count()

    increased_ambiguity = ambiguity + (0.1*same_name_party_city)
    ambiguity = np.minimum(1.0, increased_ambiguity)
    return ambiguity