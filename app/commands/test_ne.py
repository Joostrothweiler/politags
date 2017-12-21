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
    party_scores = []
    politician_scores = []

    for output_obj in output['items']:
        for eval_obj in eval_output['items']:
            if output_obj['article_id'] == eval_obj['article_id']:

                party_scores.append(party_scorer(output_obj['parties'], eval_obj['parties']))
                politician_scores.append(politician_scorer(output_obj['politicians'], eval_obj['politicians']))

    final_scorer(party_scores, politician_scores)


def final_scorer(party_scores, politician_scores):
    party_precision_count = 0
    party_recall_count = 0
    party_output_count = 0
    party_eval_count = 0

    politician_precision_count = 0
    politician_recall_count = 0
    politician_output_count = 0
    politician_eval_count = 0

    for i in party_scores:
        party_precision_count += i['precision_count']
        party_recall_count += i['recall_count']
        party_output_count += i['output_count']
        party_eval_count += i['eval_count_simple']

    for i in politician_scores:
        politician_precision_count += i['precision_count']
        politician_recall_count += i['recall_count']
        politician_output_count += i['output_count']
        politician_eval_count += i['eval_count_simple']

    if party_output_count > 0:
        print('Party Precision: {}'.format(party_precision_count / party_output_count))
    if party_eval_count > 0:
        print('Party Recall: {}'.format(party_recall_count / party_eval_count))

    if politician_output_count > 0:
        print('Politician Precision: {}'.format(politician_precision_count / politician_output_count))
    if politician_eval_count > 0:
        print('Politician Recall: {}'.format(politician_recall_count / politician_eval_count))



def party_scorer(output_item_parties, eval_item_parties):
    eval_count_simple = 0
    precision_count = 0
    recall_count = 0

    for ep in eval_item_parties:
        if ep['system_id'] != 999999999:
            eval_count_simple += 1

    # Hoe veel die die heeft gevonden zijn correct (PRECISION)
    if len(output_item_parties) > 0:
        for op in output_item_parties:
            for ep in eval_item_parties:
                if op['abbreviation'] == ep['abbreviation']:
                    precision_count += 1
        precision_ratio = precision_count / len(output_item_parties)
    else:
        precision_ratio = 1.0

    # How veel die die moest vinden heeft die daadwerkelijk gevonden (RECALL)
    if eval_count_simple > 0:
        for ep in eval_item_parties:
            for op in output_item_parties:
                if op['abbreviation'] == ep['abbreviation']:
                    recall_count += 1
        recall_ratio = recall_count / eval_count_simple
    else:
        recall_ratio = 1.0

    return {
        'output_count': len(output_item_parties),
        'eval_count_simple': eval_count_simple,
        'precision_count': precision_count,
        'precision_ratio': precision_ratio,
        'recall_count': recall_count,
        'recall_ratio': recall_ratio
    }


def politician_scorer(output_item_politicians, eval_item_politicians):
    eval_count_simple = 0
    precision_count = 0
    recall_count = 0

    for ep in eval_item_politicians:
        if ep['system_id'] != "000":
            eval_count_simple += 1

    # Hoe veel die die heeft gevonden zijn correct (PRECISION)
    if len(output_item_politicians) > 0:
        for op in output_item_politicians:
            for ep in eval_item_politicians:
                if op['system_id'] == ep['system_id']:
                    precision_count += 1
        precision_ratio = precision_count / len(output_item_politicians)
    else:
        precision_ratio = 1.0

    # How veel die die moest vinden heeft die daadwerkelijk gevonden (RECALL)
    if eval_count_simple > 0:
        for ep in eval_item_politicians:
            for op in output_item_politicians:
                if op['system_id'] == ep['system_id']:
                    recall_count += 1
        recall_ratio = recall_count / eval_count_simple
    else:
        recall_ratio = 1.0

    return {
        'output_count': len(output_item_politicians),
        'eval_count_simple': eval_count_simple,
        'precision_count': precision_count,
        'precision_ratio': precision_ratio,
        'recall_count': recall_count,
        'recall_ratio': recall_ratio
    }