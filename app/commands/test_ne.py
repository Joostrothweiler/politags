import csv
import json

from flask_script import Command

from app import db
from app.models.models import Politician, Party, Question, Response, EntitiesParties, EntitiesPoliticians, Entity, \
    Article
from app.modules.entities.extract import extract_entities
from app.modules.common.utils import translate_doc


class TestNeCommand(Command):
    """ Test the NER/NED."""

    def run(self):
        test_ne()


def test_ne():
    """ Test Named Entity Algorithms."""
    print('Deleting all old data')
    remove_all_articles()
    print('Running sample articles with NER')
    init_sample_articles()


def remove_all_articles():
    # Remove all linkings
    EntitiesParties.query.delete()
    EntitiesPoliticians.query.delete()
    # Remove all entities
    Entity.query.delete()
    # Remove all articles
    Article.query.delete()


def init_sample_articles():
    samples = json.load(open('data_resources/poliflow_sample_van_dijk.json'))
    items = samples['item']

    for doc in items:
        extract_entities(translate_doc(doc))