import json
import logging

from flask_script import Command

from app.local_settings import PRODUCTION_ENVIRONMENT
from app.models.models import Verification, EntityLinking, Entity, Article, ArticleTopic
from app.modules.common.utils import translate_doc
from app.modules.enrichment.controller import process_document
from app.modules.poliflow.fetch import fetch_single_document

logger = logging.getLogger('test_ne')


class TestNeCommand(Command):
    """ Test the NER/NED."""

    def run(self):
        test_ne()


def test_ne():
    """ Test Named Entity Algorithms."""
    if not PRODUCTION_ENVIRONMENT:
        remove_all_articles()

    eval = 'data_resources/ned/evaluation/large_eval_checked.json'
    output = process_evaluation_input(eval)
    eval_output = json.load(open(eval))
    evaluate_ned(output, eval_output)


def remove_all_articles():
    logger.info('Deleting all old data')
    # Remove all verifications
    Verification.query.delete()
    # Remove all linkings
    EntityLinking.query.delete()
    # Remove all entities
    Entity.query.delete()
    # Remove topic linkings
    ArticleTopic.query.delete()
    # Remove all articles
    Article.query.delete()


def process_evaluation_input(input):
    samples = json.load(open(input))
    items = samples['items']

    output = {'items': []}

    for eval_item in items:
        article = fetch_single_document(eval_item['article_id'])
        simple_doc = translate_doc(article)
        res = process_document(simple_doc)
        logger.info('Processed article {}'.format(simple_doc['id']))
        output['items'].append(res)

    logger.info('Number of articles processing: {}'.format(len(output['items'])))
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
        logger.info('Party Precision: {}'.format(party_precision_count / party_output_count))
    if party_eval_count > 0:
        logger.info('Party Recall: {}'.format(party_recall_count / party_eval_count))

    if politician_output_count > 0:
        logger.info('Politician Precision: {}'.format(politician_precision_count / politician_output_count))
    if politician_eval_count > 0:
        logger.info('Politician Recall: {}'.format(politician_recall_count / politician_eval_count))


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
        if ep['system_id'] != 999999999:
            eval_count_simple += 1

    # Hoe veel die die heeft gevonden zijn correct (PRECISION)
    found_system_ids = [obj['system_id'] for obj in output_item_politicians]
    wrongly_found_system_ids = []
    unfound_system_ids = [obj['system_id'] for obj in eval_item_politicians]

    if len(output_item_politicians) > 0:
        for op in output_item_politicians:
            correct = False
            for ep in eval_item_politicians:
                if op['system_id'] == ep['system_id']:
                    precision_count += 1
                    correct = True
            if not correct:
                wrongly_found_system_ids.append(op['system_id'])
        precision_ratio = precision_count / len(output_item_politicians)
    else:
        precision_ratio = 1.0

    # How veel die die moest vinden heeft die daadwerkelijk gevonden (RECALL)
    if eval_count_simple > 0:
        for ep in eval_item_politicians:
            for op in output_item_politicians:
                if op['system_id'] == ep['system_id']:
                    recall_count += 1
                    unfound_system_ids.remove(ep['system_id'])
        recall_ratio = recall_count / eval_count_simple
    else:
        recall_ratio = 1.0

    logger.info('-')
    logger.info('FOUND: {}'.format(found_system_ids))
    logger.info('WRONG: {}'.format(wrongly_found_system_ids))
    logger.info('LEFT UNFOUND: {}'.format(unfound_system_ids))

    res = {
        'output_count': len(output_item_politicians),
        'eval_count_simple': eval_count_simple,
        'precision_count': precision_count,
        'precision_ratio': precision_ratio,
        'recall_count': recall_count,
        'recall_ratio': recall_ratio
    }

    return res
