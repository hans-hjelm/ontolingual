from docopt import docopt
from graph_tool.all import *
import xml.etree.ElementTree as ET


class EurovocOntobuilder:
    """
    Reads Eurovoc ``desc_thes.xml`` and ``relation_bt.xml`` files and saves them as graph-tool binary format graphs.
    """

    def __init__(self):
        self.ontology = Graph()
        self.onto_labels = self.ontology.new_vertex_property('string')
        self.ontology.vertex_properties['vertex_labels'] = self.onto_labels
        self.term_id_to_vertex_id = dict()
        self.vertex_counter = 0
        self.root = self.ontology.add_vertex()
        self.onto_labels[self.root] = 'root'
        self.term_id_to_vertex_id['root'] = self.vertex_counter
        self.vertex_counter += 1
        self.id_to_term = dict()

    def process_thesauri(self, thesaurus_filename):
        thes_tree = ET.parse(thesaurus_filename)
        thes_root = thes_tree.getroot()
        for record in thes_root.findall('RECORD'):
            thes_id = record.find('THESAURUS_ID').text.lower()
            domain_id = thes_id[:2]
            descripteur_id = record.find('DESCRIPTEUR_ID').text.lower()
            topterm = record.find('TOPTERM').text.lower()
            if domain_id not in self.term_id_to_vertex_id.keys():
                domain_node = self.add_vertex(domain_id)
                self.ontology.add_edge(self.root, domain_node)
            if thes_id not in self.term_id_to_vertex_id.keys():
                thes_node = self.add_vertex(thes_id)
                domain_node = self.ontology.vertex(self.term_id_to_vertex_id[domain_id])
                self.ontology.add_edge(domain_node, thes_node)
            if topterm == 'o':
                desc_node = self.add_vertex(descripteur_id)
                thes_node = self.ontology.vertex(self.term_id_to_vertex_id[thes_id])
                self.ontology.add_edge(thes_node, desc_node)

    def process_relations(self, relations_filename):
        thes_tree = ET.parse(relations_filename)
        thes_root = thes_tree.getroot()
        for record in thes_root.findall('RECORD'):
            upper_id = record.find('CIBLE_ID').text.lower()
            lower_id = record.find('SOURCE_ID').text.lower()
            if upper_id in self.term_id_to_vertex_id.keys():
                upper_node = self.ontology.vertex(self.term_id_to_vertex_id[upper_id])
            else:
                upper_node = self.add_vertex(upper_id)
            if lower_id in self.term_id_to_vertex_id.keys():
                lower_node = self.ontology.vertex(self.term_id_to_vertex_id[lower_id])
            else:
                lower_node = self.add_vertex(lower_id)
            self.ontology.add_edge(upper_node, lower_node)

    def add_vertex(self, term_id):
        node = self.ontology.add_vertex()
        self.onto_labels[node] = term_id
        self.term_id_to_vertex_id[term_id] = self.vertex_counter
        self.vertex_counter += 1
        return node

    def save_ontology(self, filename):
        self.ontology.save(filename, 'gt')


def main():
    args = docopt("""
    Usage:
        eurovoc_ontobuilder.py <thesaurus> <relations>
    """)
    oc = EurovocOntobuilder()
    oc.process_thesauri(args['<thesaurus>'])
    oc.process_relations(args['<relations>'])
    oc.save_ontology('eurovoc_ontology.gt')


if __name__ == '__main__':
    main()
