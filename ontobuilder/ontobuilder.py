from docopt import docopt
from graph_tool.all import *
from operator import itemgetter


class Ontobuilder:

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
        self.hyper_probs = list()
        self.cohyp_probs = list()
        self.lookup_hyp_probs = dict()
        self.lookup_co_probs = dict()
        #self.prob_threshold = 0.0001
        self.prob_threshold = 0.5
        self.forbidden_hyp = set()
        self.forbidden_co = set()
        self.candidate_list_size = 1000
        self.score_threshold = 1.0
        self.abstract_node_counter = 0

    def read_relation_scores(self, hyperonym_probs, cohyponym_probs, term_to_id):
        with open(term_to_id) as tti:
            for line in tti:
                (term, id) = line.strip().split('\t')[0].split('#')
                self.id_to_term[id] = term
        with open(hyperonym_probs) as hp:
            for line in hp:
                (id_pair, prob) = line.strip().split('\t')
                if float(prob) > self.prob_threshold:
                    self.hyper_probs.append((id_pair, float(prob)))
                    self.lookup_hyp_probs[id_pair] = float(prob)
            self.hyper_probs.sort(key=itemgetter(1), reverse=True)
        with open(cohyponym_probs) as cp:
            for line in cp:
                (id_pair, prob) = line.strip().split('\t')
                if float(prob) > self.prob_threshold:
                    self.cohyp_probs.append((id_pair, float(prob)))
                    self.lookup_co_probs[id_pair] = float(prob)
            self.cohyp_probs.sort(key=itemgetter(1), reverse=True)

    def build_ontology(self):
        (ids, score, relation) = self.find_best_relation()
        while score > self.score_threshold:
            (id1, id2) = ids.split('-')
            if id1 in self.term_id_to_vertex_id.keys():
                node1 = self.ontology.vertex(self.term_id_to_vertex_id[id1])
            else:
                node1 = None
            if id2 in self.term_id_to_vertex_id.keys():
                node2 = self.ontology.vertex(self.term_id_to_vertex_id[id2])
            else:
                node2 = None
            if relation == 'hyperonym':
                print(relation + ': ' + ids + ' prob: ' + str(self.lookup_hyp_probs[ids]) + ' score: ' + str(score)
                      + ' ### ' + self.id_to_term[id1] + ' -> ' + self.id_to_term[id2])
                if not node1 and not node2:
                    node1 = self.add_vertex(id1)
                    node2 = self.add_vertex(id2)
                    self.ontology.add_edge(self.root, node1)
                    self.ontology.add_edge(node1, node2)
                elif not node2:
                    node2 = self.add_vertex(id2)
                    self.ontology.add_edge(node1, node2)
                else:
                    if not node1:
                        node1 = self.add_vertex(id1)
                        self.ontology.add_edge(self.root, node1)
                    parent2 = self.get_onto_parent_id(id2)
                    if parent2 == 'root':
                        self.delete_parent_edge(id2)
                        self.ontology.add_edge(node1, node2)
                    elif parent2.startswith('abstractnode'):
                        parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                        delete_edges = list()
                        for edge in parent2_node.get_out_edges(parent2_node):
                            self.ontology.add_edge(node1, edge.target())
                            delete_edges.append(edge)
                        self.remove_edges(delete_edges)
                        self.delete_parent_edge(parent2)
                        #self.ontology.remove_vertex(parent2_node)
            elif relation == 'cohyponym':
                print(relation + ': ' + ids + ' prob: ' + str(self.lookup_co_probs[ids]) + ' score: ' + str(score)
                      + ' ### ' + self.id_to_term[id1] + ' <-> ' + self.id_to_term[id2])
                if not node1 and not node2:
                    node1 = self.add_vertex(id1)
                    node2 = self.add_vertex(id2)
                    self.abstract_node_counter += 1
                    abstract_parent = self.add_vertex('abstractnode_' + str(self.abstract_node_counter))
                    self.ontology.add_edge(self.root, abstract_parent)
                    self.ontology.add_edge(abstract_parent, node1)
                    self.ontology.add_edge(abstract_parent, node2)
                elif not node2:
                    node2 = self.add_vertex(id2)
                    parent1 = self.get_onto_parent_id(id1)
                    if parent1 == 'root':
                        self.delete_parent_edge(id1)
                        self.abstract_node_counter += 1
                        abstract_parent = self.add_vertex('abstractnode_' + str(self.abstract_node_counter))
                        self.ontology.add_edge(self.root, abstract_parent)
                        self.ontology.add_edge(abstract_parent, node1)
                        self.ontology.add_edge(abstract_parent, node2)
                    else:
                        parent1_node = self.ontology.vertex(self.term_id_to_vertex_id[parent1])
                        self.ontology.add_edge(parent1_node, node2)
                elif not node1:
                    node1 = self.add_vertex(id1)
                    parent2 = self.get_onto_parent_id(id2)
                    if parent2 == 'root':
                        self.delete_parent_edge(id2)
                        self.abstract_node_counter += 1
                        abstract_parent = self.add_vertex('abstractnode_' + str(self.abstract_node_counter))
                        self.ontology.add_edge(self.root, abstract_parent)
                        self.ontology.add_edge(abstract_parent, node1)
                        self.ontology.add_edge(abstract_parent, node2)
                    else:
                        parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                        self.ontology.add_edge(parent2_node, node1)
                else:
                    parent1 = self.get_onto_parent_id(id1)
                    parent2 = self.get_onto_parent_id(id2)
                    if parent1 == 'root' and parent2 == 'root':
                        self.delete_parent_edge(id1)
                        self.delete_parent_edge(id2)
                        self.abstract_node_counter += 1
                        abstract_parent = self.add_vertex('abstractnode_' + str(self.abstract_node_counter))
                        self.ontology.add_edge(self.root, abstract_parent)
                        self.ontology.add_edge(abstract_parent, node1)
                        self.ontology.add_edge(abstract_parent, node2)
                    elif parent1 == 'root':
                        self.delete_parent_edge(id1)
                        parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                        self.ontology.add_edge(parent2_node, node1)
                    elif parent2 == 'root':
                        self.delete_parent_edge(id2)
                        parent1_node = self.ontology.vertex((self.term_id_to_vertex_id[parent1]))
                        self.ontology.add_edge(parent1_node, node2)
                    elif parent2.startswith('abstractnode'):
                        parent1_node = self.ontology.vertex(self.term_id_to_vertex_id[parent1])
                        parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                        delete_edges = list()
                        for edge in parent2_node.get_out_edges():
                            self.ontology.add_edge(parent1_node, edge.target())
                            delete_edges.append(edge)
                        self.remove_edges(delete_edges)
                        self.delete_parent_edge(parent2)
                        #self.ontology.remove_vertex(parent2_node)
                    elif parent1.startswith('abstractnode'):
                        parent1_node = self.ontology.vertex(self.term_id_to_vertex_id[parent1])
                        parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                        delete_edges = list()
                        for edge in parent1_node.get_out_edges():
                            self.ontology.add_edge(parent2_node, edge.target())
                            delete_edges.append(edge)
                        self.remove_edges(delete_edges)
                        self.delete_parent_edge(parent1)
                        #self.ontology.remove_vertex(parent1_node)
            (ids, score, relation) = self.find_best_relation()

    def remove_edges(self, edges):
        for edge in edges:
            self.ontology.remove_edge(edge)

    def add_vertex(self, term_id):
        node = self.ontology.add_vertex()
        self.onto_labels[node] = term_id
        self.term_id_to_vertex_id[term_id] = self.vertex_counter
        self.vertex_counter += 1
        return node

    def delete_parent_edge(self, term_id):
        node = self.ontology.vertex(self.term_id_to_vertex_id[term_id])
        edge = next(self.ontology.get_in_edges(node))
        self.ontology.remove_edge(edge)

    def find_best_relation(self):
        (hyper_ids, hyper_score) = self.find_best_specific_relation(self.hyper_probs, self.forbidden_hyp, 'hyperonym')
        (cohyp_ids, cohyp_score) = self.find_best_specific_relation(self.cohyp_probs, self.forbidden_co, 'cohyponym')
        if cohyp_score > hyper_score:
            self.remove_relation_prob('cohyponym', cohyp_ids)
            return cohyp_ids, cohyp_score, 'cohyponym'
        else:
            self.remove_relation_prob('hyperonym', hyper_ids)
            return hyper_ids, hyper_score, 'hyperonym'

    def remove_relation_prob(self, relation, ids):
        if relation == 'hyperonym':
            for i, (id_pair, _) in enumerate(self.hyper_probs):
                if id_pair == ids:
                    del self.hyper_probs[i]
                    return
        if relation == 'cohyponym':
            for i, (id_pair, _) in enumerate(self.cohyp_probs):
                if id_pair == ids:
                    del self.cohyp_probs[i]
                    break
            (id1, id2) = ids.split('-')
            rev_ids = id2 + '-' + id1
            for i, (id_pair, _) in enumerate(self.cohyp_probs):
                if id_pair == rev_ids:
                    del self.cohyp_probs[i]
                    return

    def find_best_specific_relation(self, relation_probabilities, forbidden, relation):
        top_ids = None
        top_score = 0.
        counter = 0
        for (ids, prob) in relation_probabilities:
            if counter > self.candidate_list_size:
                break
            if ids in forbidden:
                continue
            if self.check_relation(ids, relation):
                score = self.score_rel_and_delta(ids, relation)
                if score > top_score:
                    top_ids = ids
                    top_score = score
            counter += 1
        return top_ids, top_score

    def check_relation(self, ids, relation):
        (id1, id2) = ids.split('-')
        if not id2 in self.term_id_to_vertex_id.keys():
            return True
        if relation == 'hyperonym':
            parent2 = self.get_onto_parent_id(id2)
            if self.is_abstract_node(parent2):
                return True
            else:
                self.forbidden_hyp.add(ids)
                return False
        elif relation == 'cohyponym':
            if not id1 in self.term_id_to_vertex_id.keys():
                return True
            parent1 = self.get_onto_parent_id(id1)
            parent2 = self.get_onto_parent_id(id2)
            if self.is_abstract_node(parent1) or self.is_abstract_node(parent2):
                return True
            else:
                self.forbidden_co.add(ids)
                return False

    def is_abstract_node(self, id):
        return id == 'root' or id.startswith('abstractnode')

    def smallest_common_subsumer(self, id1, id2, parents1, parents2):
        parents1.add(id1)
        parents2.add(id2)
        scs = parents1.intersection(parents2)
        if len(scs) > 0:
            return scs.pop()
        parent1 = self.get_onto_parent_id(id1)
        parent2 = self.get_onto_parent_id(id2)
        if not parent1:
            return self.smallest_common_subsumer(id1, parent2, parents1, parents2)
        elif not parent2:
            return self.smallest_common_subsumer(parent1, id2, parents1, parents2)
        else:
            return self.smallest_common_subsumer(parent1, parent2, parents1, parents2)

    def get_onto_parent_id(self, id):
        the_node = self.ontology.vertex(self.term_id_to_vertex_id[id])
        if the_node.in_degree() > 0:
            parent_id = self.onto_labels[next(the_node.in_neighbours())]
            return parent_id
        return None

    def score_rel_and_delta(self, ids, relation):
        delta = self.calculate_delta(ids, relation)
        score = self.score_delta(delta)
        return score

    def calculate_delta(self, ids, relation):
        delta = list()
        delta.append((ids, relation))
        (id1, id2) = ids.split('-')
        if id1 in self.term_id_to_vertex_id.keys():
            node1 = self.ontology.vertex(self.term_id_to_vertex_id[id1])
        else:
            node1 = None
        if id2 in self.term_id_to_vertex_id.keys():
            node2 = self.ontology.vertex(self.term_id_to_vertex_id[id2])
        else:
            node2 = None
        if not node1 and not node2:
            return delta
        if relation == 'hyperonym':
            if not node2:
                parent1 = self.get_onto_parent_id(id1)
                parent1_node = self.ontology.vertex(self.term_id_to_vertex_id[parent1])
                for node in parent1_node.out_neighbours():
                    node_label = self.onto_labels[node]
                    delta.append((node_label + '-' + id2, 'cohyponym'))
            elif not node1:
                parent2 = self.get_onto_parent_id(id2)
                if not parent2.startswith('abstractnode'):
                    return delta
                parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                for node in parent2_node.out_neighbours():
                    node_label = self.onto_labels[node]
                    if node_label == id2:
                        continue
                    delta.append((id1 + '-' + node_label, 'hyperonym'))
            else:
                parent2 = self.get_onto_parent_id(id2)
                if not self.is_abstract_node(parent2):
                    return delta
                for node in node1.out_neighbours():
                    node_label = self.onto_labels[node]
                    delta.append((node_label + '-' + id2, 'cohyponym'))
                if parent2 == 'root':
                    return delta
                parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                for node in parent2_node.out_neighbours():
                    node_label = self.onto_labels[node]
                    if node_label == id2:
                        continue
                    delta.append((id1 + '-' + node_label, 'hyperonym'))
                    for node_p in node1.out_neighbours():
                        node_label_p = self.onto_labels[node_p]
                        delta.append((node_label_p + '-' + node_label, 'cohyponym'))
        elif relation == 'cohyponym':
            if not node2:
                parent1 = self.get_onto_parent_id(id1)
                if parent1 == 'root':
                    return delta
                parent1_node = self.ontology.vertex(self.term_id_to_vertex_id[parent1])
                for node in parent1_node.out_neighbours():
                    node_label = self.onto_labels[node]
                    if node_label == id1:
                        continue
                    delta.append((node_label + '-' + id2, 'cohyponym'))
                if parent1.startswith('abstractnode'):
                    return delta
                delta.append((parent1 + '-' + id2, 'hyperonym'))
            elif not node1:
                parent2 = self.get_onto_parent_id(id2)
                if parent2 == 'root':
                    return delta
                parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                for node in parent2_node.out_neighbours():
                    node_label = self.onto_labels[node]
                    if node_label == id2:
                        continue
                    delta.append((id1 + '-' + node_label, 'cohyponym'))
                if parent2.startswith('abstractnode'):
                    return delta
                delta.append((parent2 + '-' + id1, 'hyperonym'))
            else:
                parent1 = self.get_onto_parent_id(id1)
                parent2 = self.get_onto_parent_id(id2)
                if parent1 == 'root' and parent2 == 'root':
                    return delta
                elif parent2 == 'root':
                    parent1_node = self.ontology.vertex(self.term_id_to_vertex_id[parent1])
                    for node in parent1_node.out_neighbours():
                        node_label = self.onto_labels[node]
                        if node_label == id1:
                            continue
                        delta.append((node_label + '-' + id2, 'cohyponym'))
                    if parent1.startswith('abstractnode'):
                        return delta
                    delta.append((parent1 + '-' + id2, 'hyperonym'))
                elif parent1 == 'root':
                    parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                    for node in parent2_node.out_neighbours():
                        node_label = self.onto_labels[node]
                        if node_label == id2:
                            continue
                        delta.append((id1 + '-' + node_label, 'cohyponym'))
                    if parent2.startswith('abstractnode'):
                        return delta
                    delta.append((parent2 + '-' + id1, 'hyperonym'))
                elif parent1.startswith('abstractnode') or parent2.startswith('abstractnode'):
                    parent1_node = self.ontology.vertex(self.term_id_to_vertex_id[parent1])
                    parent2_node = self.ontology.vertex(self.term_id_to_vertex_id[parent2])
                    for node in parent1_node.out_neighbours():
                        node_label = self.onto_labels[node]
                        if node_label == id1:
                            continue
                        for node_p in parent2_node.out_neighbours():
                            node_label_p = self.onto_labels[node_p]
                            if node_label_p == id2:
                                continue
                            delta.append((node_label + '-' + node_label_p, 'cohyponym'))
                    if not self.is_abstract_node(parent1):
                        for node in parent2_node.out_neighbours():
                            node_label = self.onto_labels[node]
                            if node_label == id2:
                                continue
                            delta.append((parent1 + '-' + node_label, 'hyperonym'))
                    else:
                        for node in parent1_node.out_neighbours():
                            node_label = self.onto_labels[node]
                            if node_label == id1:
                                continue
                            delta.append((parent2 + '-' + node_label, 'hyperonym'))
        return delta

    def score_delta(self, deltas):
        delta_score = 1.0
        for (ids, relation) in deltas:
            if relation == 'cohyponym':
                if ids in self.lookup_co_probs.keys():
                    prob = self.lookup_co_probs[ids]
                else:
                    prob = self.prob_threshold
            elif relation == 'hyperonym':
                if ids in self.lookup_hyp_probs.keys():
                    prob = self.lookup_hyp_probs[ids]
                else:
                    prob = self.prob_threshold
            if prob == 1.0:
                prob = 1.0 - self.prob_threshold
            the_odds = prob / (1.0 - prob)
            delta_score *= the_odds
        return delta_score

    def save_ontology(self, filename):
        self.ontology.save(filename, 'gt')


def main():
    args = docopt("""
    Usage:
        ontobuilder.py <hyperonym_probs> <cohyponym_probs> <term_to_id>
    """)
    oc = Ontobuilder()
    oc.read_relation_scores(args['<hyperonym_probs>'], args['<cohyponym_probs>'], args['<term_to_id>'])
    oc.build_ontology()
    oc.save_ontology('ontology.gt')


if __name__ == '__main__':
    main()
