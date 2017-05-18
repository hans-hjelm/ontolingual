#!/usr/bin/env bash

#echo "train the hyperonym classifier"
#python3 ontoclassifier/ontoclassifier.py data/hyper_features.tsv logistic_regression data/hyper_probs_lr.tsv
#echo "train the cohyponym classifier"
#python3 ontoclassifier/ontoclassifier.py data/cohyp_features.tsv logistic_regression data/cohyp_probs_lr.tsv
echo "iteratively build the ontology"
python3 ontobuilder/ontobuilder.py data/hyper_probs_lr.tsv data/cohyp_probs_lr.tsv data/term_freqs_22.tsv
#echo "build the gold standard ontology"
#python3 ontobuilder/eurovoc_ontobuilder.py <desc_thes.xml> <relation_bt.xml>
echo "evaluate the ontology against the gold standard"
python3 ontoeval/path_length_pmcc.py data/eurovoc_ontology.gt data/ontology.gt
