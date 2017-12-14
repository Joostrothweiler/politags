import json

from flask_script import Command

from app.models.models import EntitiesParties, EntitiesPoliticians, Entity, Article
from app.modules.common.utils import translate_doc
from app.modules.entities.named_entity_linking import process_document


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
        process_document(translate_doc(doc))