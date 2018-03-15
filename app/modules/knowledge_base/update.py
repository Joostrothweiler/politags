import csv
import logging

from app import db
from app.models.models import Politician, Party
from app.modules.knowledge_base.get_almanak import get_all_current_ministers, get_all_current_local_politicians
from app.modules.knowledge_base.get_kamerleden import get_all_current_members_of_chamber

logger = logging.getLogger('update')


def init_knowledge_base():
    logger.info('Initializing politicians')
    init_politicians()
    logger.info('Initializing parties')
    init_parties()


def init_politicians():
    with open('data_resources/politicians/politicians_enriched.csv') as csv_file:
        politicians = csv.DictReader(csv_file, delimiter=',')
        for person in politicians:
            find_or_create_politician(person)
    db.session.commit()


def init_parties():
    with open('data_resources/wiki_parties.csv') as csv_file:
        parties = csv.DictReader(csv_file, delimiter=',')
        for row in parties:
            name = row['name']
            abbreviation = row['abbreviation']
            p = find_or_create_party(name, abbreviation)
    db.session.commit()


def find_or_create_party(name, abbreviation):
    """ Find existing politicians or create new one """
    party = Politician.query.filter(Party.name == name).first()
    if not party:
        party = Party(name=name, abbreviation=abbreviation)
        db.session.add(party)
    return party


def find_or_create_politician(person: dict):
    """ Find existing politicians or create new one """
    politician_by_id = Politician.query.filter(Politician.system_id == person['system_id']).first()

    politician_by_name = Politician.query.filter(Politician.last_name == person['last_name']) \
        .filter(Politician.initials == person['initials']) \
        .filter(Politician.municipality == person['municipality']) \
        .filter(Politician.party == person['party']).first()

    if politician_by_id:
        update_existing_politician_data(politician_by_id, person)
    elif politician_by_name:
        update_existing_politician_data(politician_by_name, person)
    elif len(person['last_name']) > 1:
        politician = Politician(system_id=person['system_id'],
                                title=person['title'],
                                gender=person['gender'],
                                initials=person['initials'],
                                first_name=person['given_name'],
                                last_name=person['last_name'],
                                party=person['party'],
                                municipality=person['municipality'],
                                role=person['role'])
        db.session.add(politician)
        return politician

def update_existing_politician_data(politician, person_data):
    if politician.gender == 'unknown':
        politician.gender = person_data['gender']
    if len(politician.first_name) < 1:
        politician.first_name = person_data['given_name']
    if len(politician.party) < 1:
        politician.party = person_data['party']
    if len(politician.role) < 1:
        politician.role = person_data['role']
    db.session.add(politician)
