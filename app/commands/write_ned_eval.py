import logging
import json

import os
from flask_script import Command

from app.models.models import Article
from app.modules.entities.named_entities import return_extracted_information

logger = logging.getLogger('write_ned_eval')


class WriteNedEval(Command):
    """ Creates a boilerplate file which should be fixed/updated/checked later."""

    def run(self):
        write_ned_eval()


def write_ned_eval():
    result = {'items': []}
    items = result['items']
    articles = fetch_articles_from_db()

    for article in articles:
        # Fetch document from poliflow
        extracted_knowledge = return_extracted_information(article)
        items.append(extracted_knowledge)

    with open('data_resources/evaluation/large_eval.json', 'w') as outfile:
        json.dump(result, outfile)

    os.system("chmod 444 data_resources/evaluation/large_eval.json")


def fetch_articles_from_db():
    """
    Create function that allows us to fetch specific type/list of articles representative of the data.
    """
    articles = Article.query.all()
    return articles
