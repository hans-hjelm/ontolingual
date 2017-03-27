#!/usr/bin/env bash

CORPUS=/home/hans/corpus/dgt-aquis/en/en_part01_22.txt

########################################
# Window size 2 with "clean" subsampling
########################################
mkdir -p modeling_data
rm modeling_data/*
python3 ../hyperwords/hyperwords/corpus2pairs.py --win 2 --sub 1e-5 --thr 10 ${CORPUS} > modeling_data/pairs
../hyperwords/scripts/pairs2counts.sh modeling_data/pairs > modeling_data/counts
python3 ../hyperwords/hyperwords/counts2vocab.py modeling_data/counts

# Calculate PMI matrices for each collection of pairs
python3 ../hyperwords/hyperwords/counts2pmi.py --cds 0.75 modeling_data/counts modeling_data/pmi

# Create embeddings with SVD
python3 ../hyperwords/hyperwords/pmi2svd.py --dim 500 --neg 5 modeling_data/pmi modeling_data/svd
cp modeling_data/pmi.words.vocab modeling_data/svd.words.vocab
cp modeling_data/pmi.contexts.vocab modeling_data/svd.contexts.vocab

# Evaluate on Word Similarity
python3 ../hyperwords/hyperwords/ws_eval.py --neg 5 PPMI modeling_data/pmi ../hyperwords/testsets/ws/ws353.txt
python3 ../hyperwords/hyperwords/ws_eval.py --eig 0 SVD modeling_data/svd ../hyperwords/testsets/ws/ws353.txt

# Evaluate on Analogies
python3 ../hyperwords/hyperwords/analogy_eval.py PPMI modeling_data/pmi ../hyperwords/testsets/analogy/google.txt
python3 ../hyperwords/hyperwords/analogy_eval.py --eig 1.25 SVD modeling_data/svd ../hyperwords/testsets/analogy/google.txt
