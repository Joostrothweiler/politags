import json
import logging
import numpy as np

from flask_script import Command

from app.local_settings import PRODUCTION_ENVIRONMENT
from app.models.models import Verification, EntityLinking, Entity, Article, ArticleTopic
from app.modules.common.utils import translate_doc
from app.modules.enrichment.controller import process_document
from app.modules.enrichment.named_entities.disambiguation import get_candidate_politicians, get_candidate_parties
from app.modules.poliflow.fetch import fetch_single_document

logger = logging.getLogger('test_candidates')


class TestCandidatesCommand(Command):
    """ Test the NER/NED."""

    def run(self):
        test_candidates()


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

def test_candidates():
    """ Test Named Entity Algorithms."""
    eval = 'data_resources/ned/evaluation/large_eval_checked.json'
    samples = json.load(open(eval))
    items = samples['items']

    if not PRODUCTION_ENVIRONMENT:
        remove_all_articles()

    candidates_per_article = get_all_candidate_per_article(items)
    score_politician_candidates(candidates_per_article, items)
    score_party_candidates(candidates_per_article, items)


def score_politician_candidates(candidates_per_article, items):
    recall_scores = []
    count_eval_politicians = 0
    count_candidate_politicians = 0

    for item in items:
        article_id = item['article_id']
        politician_weight = 0
        recall_score = 0


        for p in item['politicians']:
            if not p['system_id'] == 999999999:
                politician_weight += 1

                count_eval_politicians += 1
                count_candidate_politicians += len(candidates_per_article[article_id]['politicians'])

                if p['system_id'] in candidates_per_article[article_id]['politicians']:
                    recall_score += 1
                else:
                    print(article_id)
                    print(p)

        if politician_weight > 0:
            recall_scores.append({'weight' : politician_weight, 'recall' : recall_score / politician_weight})

    total_recall_weight = 0
    final_recall_sum = 0

    for recall_score in recall_scores:
        total_recall_weight += recall_score['weight']
        final_recall_sum += (recall_score['weight'] * recall_score['recall'])

    final_recall = final_recall_sum / total_recall_weight

    print('Politician eval count: {}'.format(count_eval_politicians))
    print('Politician candidate count: {}'.format(count_candidate_politicians))
    print('Politician recall: {}'.format(final_recall))

def score_party_candidates(candidates_per_article, items):
    recall_scores = []
    count_eval_parties = 0
    count_candidate_parties = 0

    for item in items:
        article_id = item['article_id']
        party_weight = 0
        recall_score = 0

        for p in item['parties']:
            if not p['system_id'] == 999999999:
                party_weight += 1

                count_eval_parties += 1
                count_candidate_parties += len(candidates_per_article[article_id]['parties'])

                if p['abbreviation'] in candidates_per_article[article_id]['parties']:
                    recall_score += 1
                else:
                    print(article_id)
                    print(p)

        if party_weight > 0:
            recall_scores.append({'weight': party_weight, 'recall': recall_score / party_weight})

    total_recall_weight = 0
    final_recall_sum = 0

    for recall_score in recall_scores:
        total_recall_weight += recall_score['weight']
        final_recall_sum += (recall_score['weight'] * recall_score['recall'])

    final_recall = final_recall_sum / total_recall_weight

    print('Party eval count: {}'.format(count_eval_parties))
    print('Party candidate count: {}'.format(count_candidate_parties))
    print('Party recall: {}'.format(final_recall))


def get_all_candidate_per_article(items):
    output = {}

    for eval_item in items:
        doc = fetch_single_document(eval_item['article_id'])
        simple_doc = translate_doc(doc)
        process_document(simple_doc)

        article = Article.query.filter(Article.id == eval_item['article_id']).first()

        politicians = []
        parties = []

        for entity in article.entities:
            if entity.label == 'PER':
                for candidate in get_candidate_politicians(entity):
                    politicians.append(candidate.system_id)
            elif entity.label == 'ORG':
                for candidate in get_candidate_parties(entity):
                    parties.append(candidate.abbreviation)

        output[eval_item['article_id']] = {'politicians' : np.unique(politicians), 'parties' : np.unique(parties)}
    return output
