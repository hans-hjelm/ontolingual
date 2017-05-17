#!/usr/bin/env bash

echo "iteratively build the ontology"
python3 ontobuilder/ontobuilder.py data/hyper_probs_lr_noweight.tsv data/cohyp_probs_lr_noweight.tsv data/term_freqs_22.tsv
#echo "iteratively build the ontology"
#python3 ontobuilder/eurovoc_ontobuilder.py <desc_thes.xml> <relation_bt.xml>
echo "evaluate the ontology against the gold standard"
python3 ontoeval/path_length_pmcc.py data/eurovoc_ontology.gt data/ontology.gt
