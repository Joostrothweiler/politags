import logging
import json

from flask_script import Command

from app.models.models import ArticleTopic, Article
from app.modules.common.utils import translate_doc
from app.modules.poliflow.fetch import fetch_single_document

logger = logging.getLogger('get_topic_eval')


class GetTopicEvalCommand(Command):
    def run(self):
        labeled_articles = get_articles_of_interest()
        save_evaluation_articles(labeled_articles)
        save_unlabeled_articles(labeled_articles)


def get_articles_of_interest():
    verified_article_topics = ArticleTopic.query.filter(ArticleTopic.updated_certainty == 1).all()
    logger.info('Number of verified topics: {}'.format(len(verified_article_topics)))

    articles = []
    for article_topic in verified_article_topics:
        article = article_topic.article

        if article not in articles:
            articles.append(article)

    logger.info('Number of articles that contain verified topics: {}'.format(len(articles)))
    return articles


def save_evaluation_articles(articles):
    CERTAINTY_THRESHOLD = 0.95

    result = []
    for article in articles:
        doc = fetch_single_document(article.id)
        simple_doc = translate_doc(doc)
        content = simple_doc['text_description']

        article_topics = ArticleTopic.query.filter(ArticleTopic.article_id == article.id).filter(
            ArticleTopic.updated_certainty > CERTAINTY_THRESHOLD).all()

        topics = []
        for article_topic in article_topics:
            topics.append(article_topic.topic.name)

        result.append({'article_id': article.id, 'categories': topics, 'content': content})

    save_data(result, 'labeled_data_{}'.format(CERTAINTY_THRESHOLD))


def save_unlabeled_articles(labeled_articles):
    result = []

    labeled_article_ids = []
    for article in labeled_articles:
        labeled_article_ids.append(article.id)

    unlabeled_articles = Article.query.filter(~Article.id.in_(labeled_article_ids)).limit(2500).all()

    for unlabeled_article in unlabeled_articles:
        doc = fetch_single_document(unlabeled_article.id)
        simple_doc = translate_doc(doc)
        content = simple_doc['text_description']
        result.append({'article_id': unlabeled_article.id, 'content': content})

    save_data(result, 'unlabeled')


def save_data(data, file_name):
    with open('data_resources/topics/kamerstukken/poliflw_target_{}.json'.format(file_name), 'w') as outfile:
        json.dump(data, outfile)
