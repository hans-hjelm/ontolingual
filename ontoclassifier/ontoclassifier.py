from docopt import docopt
import numpy as np
import pandas as pd
import pylab as pl
import matplotlib.pyplot as plt
from patsy import dmatrices
from sklearn.ensemble import RandomForestClassifier as rfc
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict


class Ontoclassifier:

    def __init__(self):
        pass

    def train_hyper_logreg(self, data_file, outfile):
        # read in hyperonym data
        hdf = pd.read_csv(data_file, delimiter='\t', header=0)
        #print(pd.crosstab(hdf['label'], hdf['freq_diff'], rownames=['label']))
        #hdf.hist()
        #pl.show()

        y, X = dmatrices('label ~ freq_word1 + freq_word2 + freq_diff + similarity_pmi + similarity_svd + context_subsumption \
                          + context_entropy_word1 + context_entropy_word2 + entropy_diff + normalized_entropy_w1 + \
                          normalized_entropy_w2 + normalized_entropy_diff', hdf, return_type='dataframe')
        y = np.ravel(y)

        model = LogisticRegression()
        model.fit(X, y)
        print(model.coef_)
        predicted = cross_val_predict(LogisticRegression(), X, y, cv=10, verbose=1)
        #print(metrics.roc_auc_score(y, predicted))
        i = 0
        ids = np.ravel(hdf.get('id'))
        with open(outfile, 'w') as of:
            while i < len(predicted):
                of.write(ids[i] + '\t' + str(predicted[i]) + '\n')
                i += 1
        #scores = cross_val_score(LogisticRegression(), X, y, scoring='roc_auc', cv=10)
        #scores = 2 * scores - 1
        #print(scores)
        #print('avg gini: ' + str(scores.mean()) + ' stdev: ' + str(scores.std()))

    def train_hyper_random_forest(self, data_file, outfile):
        hdf = pd.read_csv(data_file, delimiter='\t', header=0)

        y, X = dmatrices('label ~ freq_word1 + freq_word2 + freq_diff + similarity_pmi + similarity_svd + context_subsumption \
                          + context_entropy_word1 + context_entropy_word2 + entropy_diff + normalized_entropy_w1 + \
                          normalized_entropy_w2 + normalized_entropy_diff', hdf, return_type='dataframe')
        y = np.ravel(y)

        clf = rfc(n_estimators=10, verbose=2, random_state=12, class_weight=None)

        predicted = cross_val_predict(clf, X, y, cv=3, verbose=2, method='predict_proba')
        print(metrics.roc_auc_score(y, predicted))
        i = 0
        ids = np.ravel(hdf.get('id'))
        with open(outfile, 'w') as of:
            while i < len(predicted):
                of.write(ids[i] + '\t' + str(predicted[i]) + '\n')
                i += 1
        scores = cross_val_score(clf, X, y, scoring='roc_auc', cv=3)
        scores = 2 * scores - 1
        print(scores)
        print('avg gini: ' + str(scores.mean()) + ' stdev: ' + str(scores.std()))


def main():
    args = docopt("""
    Usage:
        ontoclassifier.py <data_file> <relation> <classifier> <output>
    """)
    oc = Ontoclassifier()
    if args['<relation>'] == 'hyperonymy':
        if args['<classifier>'] == 'logistic_regression':
            oc.train_hyper_logreg(args['<data_file>'], args['<output>'])
        if args['<classifier>'] == 'random_forest':
            oc.train_hyper_random_forest(args['<data_file>'], args['<output>'])


if __name__ == '__main__':
    main()
