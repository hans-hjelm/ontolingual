# ontolingual
Ontolingual provides code for going from a corpus to a terminological ontology, using distributional semantics to learn relations. It also provides code for calculating a correlation measure between two ontologies, based on shortest path distances between common entries. This repo is premierly intended for research purposes, rather than for production.

## Getting started
You need two things for this code to be of use: a gold standard ontology from which to learn typical relational patterns between words/terms, and a text collection containing those words (newspaper articles, dictionary entries, blogposts, or whatever). This library will process the terms and texts in different steps in order to produce the learned ontology. Using the gold standard ontology, it can also calculate a correlation measure between the learned ontlogy and the gold standard.

Here is a [presetation](https://docs.google.com/presentation/d/1sBr6BH7fFdWgIosr9O77p-l_cFqTy9yFtRA0jKm5kj0/pub?start=true&loop=false&delayms=5000) I gave at the Univeristy of Zurich on the topic, for overview.

In all examples I have used [Eurovoc](http://eurovoc.europa.eu/) as list of terms **and** ontology gold standard, and I have used the [JRC Acquis V3](https://ec.europa.eu/jrc/en/language-technologies/jrc-acquis) as my corpus.

Here follows a brief descrition of each step:

* Preprocessing. It is assumed that you have a mapping between terms and IDs for the terms that you wish to analyze. The mapping should be stared in a tab-separated .tsv file, the first column containing the term, and the second containing the term's unique ID. The `preprocess/parse_ontology.py` script will do this for you if you are using Eurovoc:

```bash
python3 preprocess/parse_ontology.py <desc_en.xml> > parsed_ontology.tsv
```

* More preprocessing. Once there is a mapping from term to unique IDs, you run a term spotting script, that will mark the occurrence of each term in the text by tagging it with its ID and replacing whitespace with underscore. For example, "nuclear fission" will become "nuclear_fission#1023". it will also lowercase the text and reomove non-alphanumeric characters. Run it like this:

```bash
python3 preprocess/term_spotting.py <parsed_ontology.tsv> <corpus.txt> > prepped_corpus.txt
```

* Train distributional semantics models. This library relies on the [hyperwords](https://bitbucket.org/omerlevy/hyperwords) repo by Omer Levy. I have a [fork](https://github.com/hans-hjelm/hyperwordshh) which works under python3 and adds some additional functionality; you need to install my fork in order for ontolingual to work properly. There is an example shellscript available in this repo called `hyperwd_dgtacquis.sh` - you can use this as a blueprint when training your distributional semantics model (a.k.a. word embeddings). This will produce data in a local directory called `modelling_data` (created if it does not exist, emptied if it does).

* Create features for training a model. This step requires two types of input data. The first is a gold standard ontology - in the code it is assumed that this is provided in XML format, with each record linking a narrower term to a broader term. In Eurovoc this file is called `relation_bt.xml`. The second input is the output directory created in the previous step, `modelling_data`. Two output files are produced, one called `hyper_features.tsv` (for training a hyperononmy-recognizing classifier) and one called `cohyp_features.tsv` (for training a cohyponymy-recognizing classifier). Each row in the files has a pair of ids as its first column, the label as its second column, and a number of distributional features following that. Here is how to run the script:

```bash
python3 ontofeature/feature_generator.py <relation_bt.xml> <modelling_data>
```

* Train a classifier and score term pairs. Convenience methods for training three types of classifiers are provided: logistic regression, random forest, and gradient boosted decision trees. Models are trained and evaluated using n-fold cross validation, and the Gini of the model is written to standard out. The script takes three argusments: first is the output from the previous step (for example, `hyper-features.tsv`), second is the classifier type, and third is the name of the output file. Each term pair gets a probability that the respective relation holds between the terms (hyperonymy and cohyponymy).

```bash
python3 ontoclassifier/ontoclassifier.py <hyper-features.tsv> <classifier-type> <output-file>
```

* Build the ontology. Use the output data from the previous step to iteratively build the ontology by adding one relation at a time. Adding a relation between two terms in the ontology will often imply a set of other relations that will hold after the relation has been added. This set of implied relations is scored (along with the relation itself), and the relation resulting in the highest score for both implied relations and the relation itself, gets added in each step. The resulting ontology is saved in a binary format as provided by the python graph library [graph-tool](https://graph-tool.skewed.de/). The first two arguments to the script are the output files produced in the previous step. It also takes a mapping from terms to ids as argument, in order to be able to output a graph with terms as labels instead of ids (not yet implemented). Call the script like this:

```bash
python3 ontobuilder/ontobuilder.py <hyperonym_probs_file> <cohyponym_probs_file> <term_to_id>
```

* Transform the gold standard to graph-tool binary format. This script reads in a gold standard ontology in xml format and saves it graph-tool binary format. The first argument points to a thesaurus file, which in this case assigns each term to one of 21 different domains, and to one of 127 subtopics. The second file is the `relation_bt.xml` file, described above.

```
python3 ontobuilder/eurovoc_ontobuilder.py <desc_thes.xml> <relation_bt.xml>
```

* Evaluate against the gold standard. This script calculates the shortest path between each term pair in the learned ontology. It then does the same for those term pairs in the gold standard. The lists containing the path lengths are then correlated using Pearson's coefficient, and the number of terms in the learned ontology is also reported. Call the script like this (the result is printed to the screen):

```bash
python3 ontoeval/path_length_pmcc.py <gold_standard_ontology> <learned_ontology>
```

## Prerequisites
ontolingual is written to work with Python 3. You will need the following libraries:

* cython
* docopt
* graph-tool -- install via packet manager
* hyperwords -- you need the version of hyperwords, that I have forked [here](https://github.com/hans-hjelm/hyperwordshh), which works with Python 3.
* NumPy
* pandas
* scikit-learn
* SciPy
* sparsesvd

## Versioning
The project uses semantic versioning.

## Authors
* Hans Hjelm

## Acknowledgements
* As mentioned, Omer Levy's `hyperwords` project provides the ditributional semantics implementation.
* This project builds on work that I published in my [PhD thesis](http://su.diva-portal.org/smash/record.jsf?dswid=3177&pid=diva2%3A200238&c=3&searchType=SIMPLE&language=en&query=hans+hjelm%27&af=%5B%5D&aq=%5B%5B%5D%5D&aq2=%5B%5B%5D%5D&aqe=%5B%5D&noOfRows=50&sortOrder=author_sort_asc&onlyFullText=false&sf=all).
