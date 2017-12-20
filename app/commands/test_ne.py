import json

from flask_script import Command

from app import post_article_ner
from app.models.models import Entity, Article, EntityLinking
from app.modules.common.utils import translate_doc
from app.modules.entities.named_entities import process_document


class TestNeCommand(Command):
    """ Test the NER/NED."""

    def run(self):
        test_ne()


def test_ne():
    """ Test Named Entity Algorithms."""
    print('Deleting all old data')
    remove_all_articles()

    input = 'data_resources/evaluation/van_dijk_input.json'
    output = process_evaluation_input(input)

    eval = 'data_resources/evaluation/van_dijk_eval.json'
    eval_output = json.load(open(eval))

    evaluate_ned(output, eval_output)


def remove_all_articles():
    # Remove all linkings
    EntityLinking.query.delete()
    # Remove all entities
    Entity.query.delete()
    # Remove all articles
    Article.query.delete()


def process_evaluation_input(input):
    samples = json.load(open(input))
    items = samples['items']

    output = {'items': []}

    for doc in items:
        simple_doc = translate_doc(doc)
        res = process_document(simple_doc)
        output['items'].append(res)

    return output

def evaluate_ned(output, eval_output):
    res = 0

    for output_obj in output['items']:
        for eval_obj in eval_output['items']:

            if output_obj['article_id'] == eval_obj['article_id']:

                # Loop over parties
                precision_parties_score = precision_parties(output_obj['parties'], eval_obj['parties'])
                print(precision_parties_score)

                # Loop over people


# How many in the output should actually be in there
def precision_parties(output_item_parties, eval_item_parties):
    eval_count = len(eval_item_parties)
    eval_count_simple = 0
    output_score = 0

    for op in output_item_parties:
        for ep in eval_item_parties:
            if op['abbreviation'] == ep['abbreviation']:
                output_score += 1

    for ep in eval_item_parties:
        if ep['system_id'] != "000":
            eval_count_simple += 1

    return {
        'eval_count': eval_count,
        'eval_count_simple': eval_count_simple,
        'output_score': output_score
    }


# How many of the eval are actually in the output
def recall_parties(output, eval):
    return 0