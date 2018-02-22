import logging
import time
from flask_script import Command

from app.modules.common.utils import translate_doc
from app.modules.enrichment.named_entities.controller import process_document
from app.modules.poliflow.fetch import fetch_latest_documents

logger = logging.getLogger('test_poliflow')

class TestPoliflowCommand(Command):
    """ Test the NER/NED."""

    def run(self):
        test_poliflow()


def test_poliflow():
    """ Test Named Entity Algorithms."""
    n_documents = 500
    documents = fetch_latest_documents(n_documents)

    start = time.time()

    for document in documents:
        process_article(document)

    end = time.time()
    time_diff = (end - start)

    logger.info('n_documents == len(documents): {}'.format(len(documents) == n_documents))
    logger.info('Time elapsed for {} documents: {}'.format(len(documents), time_diff))
    logger.info('Average time per document: {}'.format(time_diff / len(documents)))


def process_article(document):
    simple_doc = translate_doc(document)
    process_document(simple_doc)
    logger.info('Processed document {}'.format(simple_doc['id']))