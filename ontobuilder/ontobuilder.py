from docopt import docopt
from graph_tool.all import *


class Ontobuilder:

    def __init__(self):
        self.ontology = Graph()
        self.onto_labels = self.ontology.new_vertex_property('string')
        self.ontology.vertex_properties['vertex_labels'] = self.onto_labels
        self.vertex_counter = 0
        self.root = self.ontology.add_vertex()
        self.onto_labels[self.root] = 'root'
        self.vertex_counter += 1
        self.id_to_vertex = dict()
        self.id_to_vertex[self.vertex_counter] = self.root
        self.id_to_term = dict()
        self.hyper_probs = dict()
        self.cohyp_probs = dict()

    def read_relation_scores(self, hyperonym_probs, cohyponym_probs, term_to_id):
        with open(term_to_id) as tti:
            for line in tti:
                (term, id) = line.strip().split('\t')
                self.id_to_term[id] = term
        with open(hyperonym_probs) as hp:
            for line in hp:
                (id_pair, prob) = line.strip().split('\t')
                self.hyper_probs[id_pair] = prob





def main():
    args = docopt("""
    Usage:
        ontobuilder.py <hyperonym_probs> <cohyponym_probs> <term_to_id>
    """)
    oc = Ontobuilder()


if __name__ == '__main__':
    main()
