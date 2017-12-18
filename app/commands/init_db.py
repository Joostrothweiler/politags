import csv

from flask_script import Command

from app import db
from app.models.models import Politician, Party, Question, Response, EntityLinking, Entity, Article


class InitDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_db()

def init_db():
    """ Initialize the database."""
    # # Recreate the database
    db.drop_all()
    db.create_all()
    # Initialize with parties en politicians
    print('Ready to initialize')
    print('Initializing politicians')
    init_politicians()
    print('Initializing parties')
    init_parties()

    article = Article(id='someid')
    db.session.add(article)
    party = Party.query.first()
    db.session.add(party)
    entity = Entity(article = article)
    db.session.add(entity)
    linking = EntityLinking(entity=entity, linkable_object=party)
    db.session.add(linking)

    db.session.add(entity)
    db.session.commit()

    politician = Politician.query.first()
    entity = Entity(article = article)
    db.session.add(entity)
    linking = EntityLinking(entity = entity, linkable_object = politician)
    db.session.add(linking)
    db.session.commit()

    print('Initializing questions/responses')
    init_questions_responses()


def init_questions_responses():
    linking = EntityLinking.query.first()
    question = Question(possible_answers = ['Yes', 'No'], questionable_object = linking)
    db.session.add(question)
    question = Question(possible_answers = ['Maybe', 'Nah'], questionable_object = linking)
    db.session.add(question)
    db.session.commit()

    response = Response(question_id = 1, response='Yes')
    db.session.add(response)
    response = Response(question_id = 1, response='No')
    db.session.add(response)
    db.session.commit()


def init_politicians():
    with open('data_resources/archive_politicians.csv') as csv_file:
        politicians = csv.DictReader(csv_file, delimiter=',')
        for row in politicians:
            # id,name,party,municipality
            system_id = row['id']
            first_name = row['first_name']
            last_name = row['last_name']
            party = row['party']
            municipality = row['municipality']
            role = row['role']
            p = find_or_create_politician(system_id, first_name, last_name, party, municipality, role)
    db.session.commit()


def init_parties():
    with open('data_resources/wiki_parties.csv') as csv_file:
        parties = csv.DictReader(csv_file, delimiter=',')
        for row in parties:
            name = row['name']
            abbreviation = row['abbreviation']
            p = find_or_create_party(name, abbreviation)
    db.session.commit()


def find_or_create_politician(system_id, first_name, last_name, party, municipality, role):
    """ Find existing politicians or create new one """
    politician = Politician.query.filter(Politician.last_name == last_name)\
        .filter(Politician.first_name == first_name)\
        .filter(Politician.party == party).first()

    if not politician:
        politician = Politician(system_id=system_id, first_name=first_name, last_name=last_name,
                                party=party, municipality=municipality, role=role)
        db.session.add(politician)
    return politician


def find_or_create_party(name, abbreviation):
    """ Find existing politicians or create new one """
    party = Politician.query.filter(Party.name == name).first()
    if not party:
        party = Party(name=name, abbreviation=abbreviation)
        db.session.add(party)
    return party
