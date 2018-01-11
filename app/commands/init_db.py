import csv
import logging

from flask_script import Command

from app import db
from app.models.models import Politician, Party, EntityLinking, Entity, Article

logger = logging.getLogger('init_db')


class InitDbCommand(Command):
    """ Initialize the database."""


    def run(self):
        init_db()


def init_db():
    """ Initialize the database."""
    logger.info('Creating tables in database.')
    db.create_all()
    # Initialize with parties en politicians
    logger.info('Ready to initialize')
    logger.info('Initializing politicians')
    init_politicians()
    logger.info('Initializing parties')
    init_parties()

    article = Article(id='someid')
    db.session.add(article)
    party = Party.query.first()
    db.session.add(party)
    entity = Entity(article=article)
    db.session.add(entity)
    linking = EntityLinking(entity=entity, linkable_object=party)
    db.session.add(linking)

    db.session.add(entity)
    db.session.commit()

    politician = Politician.query.first()
    entity = Entity(article=article)
    db.session.add(entity)
    linking = EntityLinking(entity=entity, linkable_object=politician)
    db.session.add(linking)
    db.session.commit()


def init_politicians():
    with open('data_resources/archive_politicians.csv') as csv_file:
        politicians = csv.DictReader(csv_file, delimiter=',')
        for row in politicians:
            # id,name,party,municipality
            system_id = row['id']
            title = row['title']
            first_name = row['first_name']
            last_name = row['last_name']
            suffix = row['suffix']
            party = row['party']
            municipality = row['municipality']
            role = row['role']
            p = find_or_create_politician(system_id, title, first_name, last_name, suffix, party, municipality, role)
            db.session.commit()

def init_parties():
    with open('data_resources/wiki_parties.csv') as csv_file:
        parties = csv.DictReader(csv_file, delimiter=',')
        for row in parties:
            name = row['name']
            abbreviation = row['abbreviation']
            p = find_or_create_party(name, abbreviation)
    db.session.commit()

def find_or_create_politician(system_id, title, first_name, last_name, suffix, party, municipality, role):
    """ Find existing politicians or create new one """
    politician = Politician.query.filter(Politician.last_name == last_name) \
        .filter(Politician.first_name == first_name) \
        .filter(Politician.party == party).first()

    if not politician:
        politician = Politician(system_id=system_id, title=title, first_name=first_name, last_name=last_name,
                                suffix=suffix, party=party, municipality=municipality, role=role)
        db.session.add(politician)
    return politician

def find_or_create_party(name, abbreviation):
    """ Find existing politicians or create new one """
    party = Politician.query.filter(Party.name == name).first()
    if not party:
        party = Party(name=name, abbreviation=abbreviation)
        db.session.add(party)
    return party
