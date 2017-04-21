from hyperwords.representations import explicit
from hyperwords.representations import embedding


class HyperwdFeature:

    def __init__(self, path):
        self.non_norm_m = explicit.Explicit(path + 'pmi', False)
        self.sim_m = explicit.PositiveExplicit(path + 'pmi', neg=5)
        self.svd_m = embedding.SVDEmbedding(path + 'svd', eig=0)

    def get_raw_vector(self, word):
        return self.non_norm_m.represent(word)

    def get_sim_vector(self, word):
        return self.sim_m.represent(word)

    def get_svd_vector(self, word):
        return self.svd_m.represent(word)

    def get_similarity(self, w1, w2):
        return self.sim_m.similarity(w1, w2)

    def get_svd_similarity(self, w1, w2):
        return self.svd_m.similarity(w1, w2)

    def get_frequency(self, word):
        return self.non_norm_m.get_word_freq(word)
