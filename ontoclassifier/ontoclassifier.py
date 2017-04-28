import numpy as np
import pandas as pd
import pylab as pl
import matplotlib.pyplot as plt
from patsy import dmatrices
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split
from sklearn import metrics
from sklearn.cross_validation import cross_val_score

# read in hyperonym data
hdf = pd.read_csv('/home/hans/tmp/hhf.tsv', delimiter='\t', header=0)
print(hdf.describe())
#print(pd.crosstab(hdf['label'], hdf['freq_diff'], rownames=['label']))
#hdf.hist()
#pl.show()
#hdf['intercept'] = 1.0

y, X = dmatrices('label ~ freq_word1 + freq_word2 + freq_diff + similarity_pmi + similarity_svd + context_subsumption \
                  + context_entropy_word1 + context_entropy_word2 + entropy_diff + normalized_entropy_w1 + \
                  normalized_entropy_w1 + normalized_entropy_diff', hdf, return_type='dataframe')

y = np.ravel(y)
