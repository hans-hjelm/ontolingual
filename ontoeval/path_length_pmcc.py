from docopt import docopt
from graph_tool.all import *
from scipy.stats import pearsonr


class PathLengthPmcc:

    def __init__(self, gold_standard_ontology_file, learned_ontology_file):
        self.gs_ontology = load_graph(gold_standard_ontology_file)
        self.ld_ontology = load_graph(learned_ontology_file)
        self.gs_path_lengths = list()
        self.ld_path_lengths = list()
        self.gs_vertex_to_label = self.gs_ontology.properties[('v', 'vertex_labels')]
        self.ld_vertex_to_label = self.ld_ontology.properties[('v', 'vertex_labels')]
        self.ld_vocabulary_size = 0
        self.max_distance = 50

    def get_shared_path_lengths(self):
        for ldv1 in self.ld_ontology.vertices():
            ldl1 = self.ld_vertex_to_label[ldv1]
            gsv1 = find_vertex(self.gs_ontology, self.gs_vertex_to_label, ldl1)
            if len(gsv1) > 0:
                gsv1 = gsv1[0]
            else:
                continue
            self.ld_vocabulary_size += 1
            print(self.ld_vocabulary_size)
            for ldv2 in self.ld_ontology.vertices():
                if ldv1 >= ldv2:
                    continue
                ldl2 = self.ld_vertex_to_label[ldv2]
                gsv2 = find_vertex(self.gs_ontology, self.gs_vertex_to_label, ldl2)
                if len(gsv2) > 0:
                    gsv2 = gsv2[0]
                else:
                    continue
                ld_length = shortest_distance(self.ld_ontology, ldv1, ldv2, max_dist=self.max_distance, directed=False)
                gs_length = shortest_distance(self.gs_ontology, gsv1, gsv2, max_dist=self.max_distance, directed=False)
                self.ld_path_lengths.append(ld_length)
                self.gs_path_lengths.append(gs_length)

    def calculate_pmcc_coefficient(self):
        (corr, p_val) = pearsonr(self.gs_path_lengths, self.ld_path_lengths)
        return corr


def main():
    args = docopt("""
    Usage:
        eurovoc_ontobuilder.py <gold_standard_ontology> <learned_ontology>
    """)
    plp = PathLengthPmcc(args['<gold_standard_ontology>'], args['<learned_ontology>'])
    plp.get_shared_path_lengths()
    correlation = plp.calculate_pmcc_coefficient()
    print('voc size: ' + str(plp.ld_vocabulary_size) + ' corr: ' + str(correlation))


if __name__ == '__main__':
    main()
