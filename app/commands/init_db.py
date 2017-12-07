import datetime
import csv

from flask import current_app
from flask_script import Command

from app import db
from app.models.models import Article, Entity, Politician, Party, Question, Response


class InitDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_db()

def init_db():
    """ Initialize the database."""
    # Recreate the database
    db.drop_all()
    db.create_all()
    # Initialize with parties en politicians
    init_politicians()
    init_parties()
    init_questions_responses()



def init_questions_responses():
    question = Question(possible_answers = ['Yes', 'No'])
    db.session.add(question)
    question = Question(possible_answers = ['Maybe', 'Nah'])
    db.session.add(question)
    db.session.commit()

    response = Response(question_id = 1, response='Yes')
    db.session.add(response)
    response = Response(question_id = 1, response='No')
    db.session.add(response)
    db.session.commit()


def init_politicians():
    with open('data_resources/politicians.csv') as csv_file:
        politicians = csv.reader(csv_file, delimiter=';', quotechar='|')
        for row in politicians:
            name = row[0]
            p = find_or_create_politician(name)
    db.session.commit()


def init_parties():
    with open('data_resources/parties.csv') as csv_file:
        parties = csv.reader(csv_file, delimiter=';', quotechar='|')
        for row in parties:
            name = row[0]
            p = find_or_create_party(name)
    db.session.commit()


def find_or_create_politician(name):
    """ Find existing politicians or create new one """
    politician = Politician.query.filter(Politician.full_name == name).first()
    if not politician:
        politician = Politician(full_name=name)
        db.session.add(politician)
    return politician


def find_or_create_party(name):
    """ Find existing politicians or create new one """
    party = Politician.query.filter(Party.name == name).first()
    if not party:
        party = Party(name=name)
        db.session.add(party)
    return party

# def find_or_create_entity(identifier, text, label):
#     """ Find existing entity or create new entity """
#     entity = Entity.query.filter(Entity.text == text).first()
#     if not entity:
#         entity = Entity(text=text, label=label)
#         db.session.add(entity)
#     return entity#
#
# def find_or_create_article(identifier, entity=None):
#     """ Find existing article or create new article """
#     article = Article.query.filter(Article.id == identifier).first()
#     if not article:
#         article = Article(id=identifier)
#         if entity:
#             article.entities.append(entity)
#         db.session.add(article)
#     return article
