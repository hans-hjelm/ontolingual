#!/usr/bin/env bash

CORPUS=/home/hans/corpus/dgt-acquis/en/en_part01_11.txt

############################################
# Window size 30 characters, ngraph length n
############################################
mkdir -p ngraph_data_4
rm ngraph_data_4/*
python3 ../hyperwords/hyperwords/corpus2ngraphs.py --len 4 --win 30 --sub 1e-5 --thr 100 --del ${CORPUS} > ngraph_data_4/pairs
../hyperwords/scripts/pairs2counts.sh ngraph_data_4/pairs > ngraph_data_4/counts
python3 ../hyperwords/hyperwords/counts2vocab.py ngraph_data_4/counts

# Calculate PMI matrix for the pairs
python3 ../hyperwords/hyperwords/counts2pmi.py --cds 0.75 ngraph_data_4/counts ngraph_data_4/pmi

# Create embeddings with SVD
python3 ../hyperwords/hyperwords/pmi2svd.py --dim 500 --neg 5 ngraph_data_4/pmi ngraph_data_4/svd
cp ngraph_data_4/pmi.words.vocab ngraph_data_4/svd.words.vocab
cp ngraph_data_4/pmi.contexts.vocab ngraph_data_4/svd.contexts.vocab

# Evaluate on Word Similarity
python3 ../hyperwords/hyperwords/ws_eval.py --neg 5 --len 4 PPMIng ngraph_data_4/pmi ../hyperwords/testsets/ws/ws353_similarity.txt
python3 ../hyperwords/hyperwords/ws_eval.py --eig 0 --len 4 SVDng ngraph_data_4/svd ../hyperwords/testsets/ws/ws353_similarity.txt
python3 ../hyperwords/hyperwords/ws_eval.py --eig 0 --len 4 --w+c SVDng ngraph_data_4/svd ../hyperwords/testsets/ws/ws353_similarity.txt
