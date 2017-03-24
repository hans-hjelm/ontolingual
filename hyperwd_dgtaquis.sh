#!/usr/bin/env bash

CORPUS=/home/hans/corpus/dgt-aquis/en/en_part01_08.txt

# Window size 2 with "clean" subsampling
mkdir -p w2.sub
rm w2.sub/*
python3 ../hyperwords/hyperwords/corpus2pairs.py --win 2 --sub 1e-5 ${CORPUS} > w2.sub/pairs
../hyperwords/scripts/pairs2counts.sh w2.sub/pairs > w2.sub/counts
python3 ../hyperwords/hyperwords/counts2vocab.py w2.sub/counts

# Calculate PMI matrices for each collection of pairs
python3 ../hyperwords/hyperwords/counts2pmi.py --cds 0.75 w2.sub/counts w2.sub/pmi

# Create embeddings with SVD
python3 ../hyperwords/hyperwords/pmi2svd.py --dim 500 --neg 5 w2.sub/pmi w2.sub/svd
cp w2.sub/pmi.words.vocab w2.sub/svd.words.vocab
cp w2.sub/pmi.contexts.vocab w2.sub/svd.contexts.vocab

# Evaluate on Word Similarity
python3 ../hyperwords/hyperwords/ws_eval.py --neg 5 PPMI w2.sub/pmi ../hyperwords/testsets/ws/ws353.txt
python3 ../hyperwords/hyperwords/ws_eval.py --eig 0.5 SVD w2.sub/svd ../hyperwords/testsets/ws/ws353.txt

# Evaluate on Analogies
python3 ../hyperwords/hyperwords/analogy_eval.py PPMI w2.sub/pmi ../hyperwords/testsets/analogy/google.txt
python3 ../hyperwords/hyperwords/analogy_eval.py --eig 0 SVD w2.sub/svd ../hyperwords/testsets/analogy/google.txt
