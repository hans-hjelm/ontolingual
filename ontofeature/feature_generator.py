import math
import ontofeature as ontf
import xml.etree.ElementTree as ET

from docopt import docopt
from hyperwd_feature import HyperwdFeature


class FeatureGenerator:
    """Reads hyperword output along with a Eurovoc ``relation_bt.xml`` file to produce training data for classifiers."""

    def __init__(self, path_to_ontology, path_to_hyperwords_dir):
        self.hwf = HyperwdFeature(path_to_hyperwords_dir)
        self.narrow_to_broad = dict()
        self.broad_to_narrow = dict()
        self.parse_ontology_rels(path_to_ontology)
        self.wfreq = dict()
        self.header = 'id\tlabel\tfreq_word1\tfreq_word2\tfreq_diff\tsimilarity_pmi\tsimilarity_svd\tcontext_subsumption\tcontext_entropy_word1\tcontext_entropy_word2\tentropy_diff\tnormalized_entropy_w1\tnormalized_entropy_w2\tnormalized_entropy_diff'
        self.freq_cutoff = 10

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
        hf.write(self.header + '\n')
        cf.write(self.header + '\n')
        with open(wordlist) as wl:
            for line in wl:
                parts = line.strip().split('\t')
                words.add(parts[0])
                self.wfreq[parts[0]] = parts[1]
        for word1 in words:
            wfreq1 = int(self.wfreq[word1])
            if wfreq1 < self.freq_cutoff:
                continue
            v1 = self.hwf.get_raw_vector(word1)
            ent1 = ontf.entropy(v1)
            ent_rel_freq1 = ent1 / math.log(wfreq1, 2)
            id1 = word1.rsplit('#', maxsplit=1)[1]
            for word2 in words:
                id2 = word2.rsplit('#', maxsplit=1)[1]
                if id1 == id2:
                    continue
                common_features = self.get_common_features(word1, word2, wfreq1, v1, ent1, ent_rel_freq1)
                if common_features == '':
                    continue
                hyper_example = self.get_hyper_features(id1, id2) + common_features
                hf.write(hyper_example + '\n')
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

    def get_common_features(self, word1, word2, wfreq1, v1, ent1, ent_rel_freq1):
        wfreq2 = int(self.wfreq[word2])
        v2 = self.hwf.get_raw_vector(word2)
        if v1.getnnz() == 0 or v2.getnnz() == 0:
            return ''
        example = '\t' + str(wfreq1) + '\t' + str(wfreq2) + '\t' + str(wfreq1 - wfreq2)
        example += '\t' + str(self.hwf.get_similarity(word1, word2))
        example += '\t' + str(self.hwf.get_svd_similarity(word1, word2))
        example += '\t' + str(ontf.context_subsumption(v1, v2))
        ent2 = ontf.entropy(v2)
        example += '\t' + str(ent1) + '\t' + str(ent2) + '\t' + str(ent1 - ent2)
        ent_rel_freq2 = ent2/math.log(wfreq2, 2)
        example += '\t' + str(ent_rel_freq1) + '\t' + str(ent_rel_freq2) + '\t' + str(ent_rel_freq1 - ent_rel_freq2)
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
