import pickle
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import Perceptron
from imblearn.over_sampling import SMOTE, ADASYN
from sklearn.calibration import CalibratedClassifierCV

from flask_script import Command


class TrainClfCommand(Command):
    """ Test the NER/NED."""

    def run(self):
        train_clf()


def train_clf():
    X_train, Y_train = initialize_from_file('features_train.txt')
    # X_resampled, Y_resampled = X_train, Y_train
    X_resampled, Y_resampled = SMOTE().fit_sample(X_train, Y_train)
    X_test, Y_test = initialize_from_file('features_test.txt')

    clf = Perceptron(class_weight="balanced")
    clf_isotonic = CalibratedClassifierCV(clf, method='isotonic')
    clf_isotonic.fit(X_resampled, Y_resampled)

    print("Training score: {}".format(clf_isotonic.score(X_train, Y_train)))
    print("Test score: {}".format(clf_isotonic.score(X_test, Y_test)))

    filename = 'app/modules/entities/nlp_model/disambiguation_model.sav'
    pickle.dump(clf_isotonic, open(filename, 'wb'))


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
