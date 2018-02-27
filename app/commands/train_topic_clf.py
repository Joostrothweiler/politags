import pickle
import json
import numpy as np
import re

from sklearn.feature_extraction.text import TfidfVectorizer

from flask_script import Command
from sklearn.linear_model import SGDClassifier
from sklearn.multiclass import OneVsRestClassifier


class TrainTopicClfCommand(Command):
    """ Test the NER/NED."""

    def run(self):
        train_topic_classifier()


def train_topic_classifier():
    corpus, y = read_data()
    transformer = TfidfVectorizer(smooth_idf=True, min_df=0.00000001, max_df=0.2, sublinear_tf=True)
    estimator = SGDClassifier(loss='log', penalty='l1', alpha=1e-6, random_state=42, max_iter=10, tol=None)

    X = transformer.fit_transform(corpus)
    clf = OneVsRestClassifier(estimator).fit(X, y)

    save_topic_classifier(clf, transformer)



def save_topic_classifier(clf, transformer):
    pickle.dump(clf, open("../app/modules/enrichment/topics/models/classifier_kamerstukken.pkl", 'wb'))
    pickle.dump(transformer, open("../app/modules/enrichment/topics/models/transformer_kamerstukken.pkl", 'wb'))

def read_data():
    file = '../data_resources/topics/kamerstukken/kamerstukken_topics_first.json'
    data_first = json.load(open(file))
    file = '../data_resources/topics/kamerstukken/kamerstukken_topics_second.json'
    data_second = json.load(open(file))

    corpus = []
    y = []

    for obj in data_first:
        if not obj['category'] == 'NOCAT' and not obj['content'] == 'NOCONTENT':
            corpus.append(obj['content'])
            y.append(obj['category'])
    for obj in data_second:
        if not obj['category'] == 'NOCAT' and not obj['content'] == 'NOCONTENT':
            corpus.append(obj['content'])
            y.append(obj['category'])

    return corpus, y