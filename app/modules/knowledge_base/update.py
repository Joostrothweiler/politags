import csv
import logging

from app import db
from app.models.models import Politician, Party
from app.modules.knowledge_base.get_almanak import get_all_current_ministers, get_all_current_local_politicians
from app.modules.knowledge_base.get_kamerleden import get_all_current_members_of_chamber

logger = logging.getLogger('update')


def update_knowledge_base():
    logger.info('Updating knowledge base')
    logger.info('Initializing politicians (and update)')
    for person in get_all_current_local_politicians():
        find_or_create_politician(person)

    for person in get_all_current_ministers():
        find_or_create_politician(person)

    for person in get_all_current_members_of_chamber():
        find_or_create_politician(person)

    db.session.commit()

    logger.info('Initializing parties (and update)')
    init_parties()


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
        .filter(Politician.municipality == person['municipality']).first()

    if politician_by_id or politician_by_name:
        return politician_by_id
    elif len(person['last_name']) > 1:
        politician = Politician(system_id=person['system_id'],
                                title=person['title'],
                                initials=person['initials'],
                                first_name=person['first_name'],
                                given_name=person['given_name'],
                                last_name=person['last_name'],
                                suffix=person['suffix'],
                                party=person['party'],
                                department=person['department'],
                                municipality=person['municipality'],
                                role=person['role'])
        db.session.add(politician)
        return politician
