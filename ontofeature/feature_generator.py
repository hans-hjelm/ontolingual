import xml.etree.ElementTree as ET
import ontofeature as ontf

from docopt import docopt
from hyperwd_feature import HyperwdFeature


class FeatureGenerator:

    def __init__(self, path_to_ontology, path_to_hyperwords_dir):
        self.hwf = HyperwdFeature(path_to_hyperwords_dir)
        self.narrow_to_broad = dict()
        self.broad_to_narrow = dict()
        self.parse_ontology_rels(path_to_ontology)
        self.wfreq = dict()

    def parse_ontology_rels(self, path_to_ontology):
        tree = ET.parse(path_to_ontology)
        root = tree.getroot()
        for record in root.findall('RECORD'):
            source = record.find('SOURCE_ID').text
            cible = record.find('CIBLE_ID').text
            self.narrow_to_broad[source] = cible
            if cible not in self.broad_to_narrow.keys():
                self.broad_to_narrow[cible] = set()
            self.broad_to_narrow[cible].add(source)

    def write_features(self, wordlist):
        words = set()
        hf = open('hyper_features.tsv', 'w')
        cf = open('cohyp_features.tsv', 'w')
        with open(wordlist) as wl:
            for line in wl:
                parts = line.strip().split('\t')
                words.add(parts[0])
                self.wfreq[parts[0]] = parts[1]
        for word1 in words:
            for word2 in words:
                id1 = word1.rsplit('#', maxsplit=1)[1]
                id2 = word2.rsplit('#', maxsplit=1)[1]
                if id1 == id2:
                    continue
                common_features = self.get_common_features(word1, word2)
                hyper_example = self.get_hyper_features(id1, id2) + common_features
                hf.write(hyper_example + '\n')
                if id1 < id2:
                    cohyp_example = self.get_cohyp_features(id1, id2) + common_features
                    cf.write(cohyp_example + '\n')
        hf.close()
        cf.close()

    def get_hyper_features(self, id1, id2):
        hyper_example = id1 + '-' + id2
        if id1 in self.broad_to_narrow.keys() and id2 in self.broad_to_narrow[id1]:
            hyper_example += '\t' + '1'
        else:
            hyper_example += '\t' + '0'
        return hyper_example

    def get_cohyp_features(self, id1, id2):
        cohyp_example = id1 + '-' + id2
        if id1 in self.narrow_to_broad.keys() and self.narrow_to_broad[id1] in self.broad_to_narrow.keys() and \
                id2 in self.broad_to_narrow[self.narrow_to_broad[id1]]:
            cohyp_example += '\t' + '1'
        else:
            cohyp_example += '\t' + '0'
        return cohyp_example

    def get_common_features(self, word1, word2):
        example = '\t' + self.wfreq[word1] + '\t' + self.wfreq[word2] + '\t' + str(int(self.wfreq[word1]) -
                                                                                   int(self.wfreq[word2]))
        example += '\t' + str(self.hwf.get_similarity(word1, word2))
        example += '\t' + str(self.hwf.get_svd_similarity(word1, word2))
        v1 = self.hwf.get_raw_vector(word1)
        v2 = self.hwf.get_raw_vector(word2)
        example += '\t' + str(ontf.context_subsumption(v1, v2))
        ent1 = ontf.entropy(v1)
        ent2 = ontf.entropy(v2)
        example += '\t' + str(ent1) + '\t' + str(ent2) + '\t' + str(ent1 - ent2)
        return example


def main():
    args = docopt("""
    Usage:
        feature_generator.py <path_to_ontology> <path_to_hyperwords_dir>
    """)
    fg = FeatureGenerator(args['<path_to_ontology>'], args['<path_to_hyperwords_dir>'])
    fg.write_features('/home/hans/workspace/ontolingual/preprocess/term_freqs_22.tsv')


if __name__ == '__main__':
    main()
