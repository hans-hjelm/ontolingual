# ontolingual
Ontolingual provides code for going from a corpus to a terminological ontology, using distributional semantics to learn relations. It also provides code for calculating a correlation measure between two ontologies, based on shortest path distances between common entries. This repo is intended for research purposes, not for production.

## Getting started
You need two things for this code to be of use: a list of words/terms that you want to order into an ontology, and a text collection containing those words (newspaper articles, dictionary entries, blogposts, or whatever). This library will process the terms and texts in different steps in order to produce the learned ontology. If you have access to a gold standard ontology, it can also calculate a correlation measure between the learned ontlogy and the gold standard.

In all examples I have used [Eurovoc](http://eurovoc.europa.eu/) as list of terms **and** ontology gold standard, and I have used the [JRC Acquis V3](https://ec.europa.eu/jrc/en/language-technologies/jrc-acquis) as my corpus.

Here follows a brief descrition of each step:

1. Preprocessing. It is assumed that you have a mapping between terms and IDs for the terms that you wish to analyze. The mapping should be stared in a tab-separated .tsv file, the first column containing the term, and the second containing the term's unique ID. The `preprocess/parse_ontology.py` script will do this for you if you are using Eurovoc:

    python3 preprocess/parse_ontology.py <desc_en.xml> > parsed_ontology.tsv

1. More preprocessing. Once there is a mapping from term to unique IDs, you run a term spotting script, that will mark the occurrence of each term in the text by tagging it with its ID and replacing whitespace with underscore. For example, "nuclear fission" will become "nuclear_fission#1023". it will also lowercase the text and reomove non-alphanumeric characters. Run it like this:

    python3 preprocess/term_spotting.py <parsed_ontology.tsv> <corpus.txt> > 

