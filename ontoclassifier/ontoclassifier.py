from docopt import docopt
import numpy as np
import pandas as pd
from patsy import dmatrices
from sklearn.ensemble import GradientBoostingClassifier as GBC
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.model_selection import cross_val_predict
from sklearn.preprocessing import scale


class Ontoclassifier:

    def __init__(self):
        self.n_fold = 3
        self.cores = 1
        self.verbosity = 2
        self.random_state = 12

    def train_logreg(self, data_file, outfile):
        hdf = pd.read_csv(data_file, delimiter='\t', header=0)

        y, X = dmatrices('label ~ freq_word1 + freq_word2 + freq_diff + similarity_pmi + similarity_svd + context_subsumption \
                          + context_entropy_word1 + context_entropy_word2 + entropy_diff + normalized_entropy_w1 + \
                          normalized_entropy_w2 + normalized_entropy_diff', hdf, return_type='dataframe')

        y = np.ravel(y)
        X = scale(X)

        clf = LogisticRegression(class_weight='balanced', solver='liblinear')
        predicted = cross_val_predict(clf, X, y, cv=self.n_fold, method='predict_proba', n_jobs=self.cores, verbose=self.verbosity)
        positive_pred = predicted[:, 1]
        print('CV Gini: ' + str(2 * metrics.roc_auc_score(y, positive_pred) - 1))
        i = 0
        ids = np.ravel(hdf.get('id'))
        with open(outfile, 'w') as of:
            while i < len(positive_pred):
                of.write(ids[i] + '\t' + str(positive_pred[i]) + '\n')
                i += 1

    def train_random_forest(self, data_file, outfile):
        hdf = pd.read_csv(data_file, delimiter='\t', header=0)

        y, X = dmatrices('label ~ freq_word1 + freq_word2 + freq_diff + similarity_pmi + similarity_svd + context_subsumption \
                          + context_entropy_word1 + context_entropy_word2 + entropy_diff + normalized_entropy_w1 + \
                          normalized_entropy_w2 + normalized_entropy_diff', hdf, return_type='dataframe')
        y = np.ravel(y)

        clf = RFC(n_estimators=300, verbose=2, random_state=self.random_state, class_weight='balanced')

        predicted = cross_val_predict(clf, X, y, cv=self.n_fold, verbose=self.verbosity, method='predict_proba', n_jobs=self.cores)
        positive_pred = predicted[:, 1]
        print('CV Gini: ' + str(2 * metrics.roc_auc_score(y, positive_pred) - 1))
        i = 0
        ids = np.ravel(hdf.get('id'))
        with open(outfile, 'w') as of:
            while i < len(positive_pred):
                of.write(ids[i] + '\t' + str(positive_pred[i]) + '\n')
                i += 1

    def train_boosted_trees(self, data_file, outfile):
        hdf = pd.read_csv(data_file, delimiter='\t', header=0)

        y, X = dmatrices('label ~ freq_word1 + freq_word2 + freq_diff + similarity_pmi + similarity_svd + context_subsumption \
                          + context_entropy_word1 + context_entropy_word2 + entropy_diff + normalized_entropy_w1 + \
                          normalized_entropy_w2 + normalized_entropy_diff', hdf, return_type='dataframe')
        y = np.ravel(y)

        clf = GBC(random_state=self.random_state, verbose=self.verbosity)

        predicted = cross_val_predict(clf, X, y, cv=self.n_fold, verbose=2, method='predict_proba', n_jobs=self.cores)
        positive_pred = predicted[:, 1]
        print('CV Gini: ' + str(2 * metrics.roc_auc_score(y, positive_pred) - 1))
        i = 0
        ids = np.ravel(hdf.get('id'))
        with open(outfile, 'w') as of:
            while i < len(positive_pred):
                of.write(ids[i] + '\t' + str(positive_pred[i]) + '\n')
                i += 1


def main():
    args = docopt("""
    Usage:
        ontoclassifier.py <data_file> <classifier> <output>
    """)
    oc = Ontoclassifier()
    if args['<classifier>'] == 'logistic_regression':
        oc.train_logreg(args['<data_file>'], args['<output>'])
    if args['<classifier>'] == 'random_forest':
        oc.train_random_forest(args['<data_file>'], args['<output>'])
    if args['<classifier>'] == 'boosted_trees':
        oc.train_boosted_trees(args['<data_file>'], args['<output>'])


if __name__ == '__main__':
    main()
