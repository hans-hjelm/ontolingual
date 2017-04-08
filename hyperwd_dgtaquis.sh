#!/usr/bin/env bash

CORPUS=/home/hans/corpus/dgt-acquis/en/en_part01_16.txt

########################################
# Window size 2 with "clean" subsampling
########################################
mkdir -p modeling_data
rm modeling_data/*
python3 ../hyperwords/hyperwords/corpus2pairs.py --win 2 --sub 1e-5 --thr 10 --del ${CORPUS} > modeling_data/pairs
../hyperwords/scripts/pairs2counts.sh modeling_data/pairs > modeling_data/counts
python3 ../hyperwords/hyperwords/counts2vocab.py modeling_data/counts

# Calculate PMI matrix for the pairs
python3 ../hyperwords/hyperwords/counts2pmi.py --cds 0.75 modeling_data/counts modeling_data/pmi

# Create embeddings with SVD
python3 ../hyperwords/hyperwords/pmi2svd.py --dim 500 --neg 5 modeling_data/pmi modeling_data/svd
cp modeling_data/pmi.words.vocab modeling_data/svd.words.vocab
cp modeling_data/pmi.contexts.vocab modeling_data/svd.contexts.vocab

# Evaluate on Word Similarity
python3 ../hyperwords/hyperwords/ws_eval.py --neg 5 PPMI modeling_data/pmi ../hyperwords/testsets/ws/ws353_similarity.txt
python3 ../hyperwords/hyperwords/ws_eval.py --eig 0 --w+c SVD modeling_data/svd ../hyperwords/testsets/ws/ws353_similarity.txt

# Evaluate on Analogies
python3 ../hyperwords/hyperwords/analogy_eval.py PPMI modeling_data/pmi ../hyperwords/testsets/analogy/google.txt
python3 ../hyperwords/hyperwords/analogy_eval.py --eig 1.25 SVD modeling_data/svd ../hyperwords/testsets/analogy/google.txt
