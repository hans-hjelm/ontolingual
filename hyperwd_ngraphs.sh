#!/usr/bin/env bash

CORPUS=/home/hans/corpus/dgt-aquis/en/en_part01.txt

############################################
# Window size 30 characters, ngraph length 3
############################################
mkdir -p ngraph_data
rm ngraph_data/*
python3 ../hyperwords/hyperwords/corpus2ngraphs.py --len 3 --win 30 --sub 1e-5 --thr 100 ${CORPUS} > ngraph_data/pairs
../hyperwords/scripts/pairs2counts.sh ngraph_data/pairs > ngraph_data/counts
python3 ../hyperwords/hyperwords/counts2vocab.py ngraph_data/counts

# Calculate PMI matrix for the pairs
python3 ../hyperwords/hyperwords/counts2pmi.py --cds 0.75 ngraph_data/counts ngraph_data/pmi

# Create embeddings with SVD
python3 ../hyperwords/hyperwords/pmi2svd.py --dim 500 --neg 5 ngraph_data/pmi ngraph_data/svd
cp ngraph_data/pmi.words.vocab ngraph_data/svd.words.vocab
cp ngraph_data/pmi.contexts.vocab ngraph_data/svd.contexts.vocab

# Evaluate on Word Similarity
python3 ../hyperwords/hyperwords/ws_eval.py --neg 5 --len 3 PPMIng ngraph_data/pmi ../hyperwords/testsets/ws/ws353.txt
python3 ../hyperwords/hyperwords/ws_eval.py --eig 0 --len 3 SVDng ngraph_data/svd ../hyperwords/testsets/ws/ws353.txt

# Evaluate on Analogies
python3 ../hyperwords/hyperwords/analogy_eval.py --len 3 PPMIng ngraph_data/pmi ../hyperwords/testsets/analogy/google.txt
python3 ../hyperwords/hyperwords/analogy_eval.py --eig 1.25 --len 3 SVDng ngraph_data/svd ../hyperwords/testsets/analogy/google.txt
