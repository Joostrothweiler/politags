import pickle
import numpy as np
from sklearn.linear_model import Perceptron
from imblearn.over_sampling import SMOTE
from sklearn.calibration import CalibratedClassifierCV

from flask_script import Command


class TrainClfCommand(Command):
    """ Test the NER/NED."""

    def run(self):
        train_clf()


def fetch_classifier_data():
    pass


def train_clf():
    # Fetch NED training/test data from database
    X, y = []
    # Train a classifier
    clf = None
    # Test the classifier

    # Only if it is actually an improvement, store the model,





    filename = 'app/modules/entities/nlp_model/disambiguation_model.sav'
    pickle.dump(clf, open(filename, 'wb'))


def initialize_from_file(filename):
    X = []
    Y = []

    with open('app/modules/entities/nlp_model/tooling/training/{}'.format(filename)) as f:
        content = f.readlines()

    for i in content:
        i = i.replace('\n', '')
        i = i.split(',')
        X.append(i[0:-1])
        Y.append(i[-1])

    X = np.float_(X, dtype=object)
    return X,Y
