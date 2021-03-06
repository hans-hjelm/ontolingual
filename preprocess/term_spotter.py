import re

from collections import Counter
from docopt import docopt


class TermSpotter:
    """
    Reads output from the ``parse_ontology.py`` script, along with a corpus, and writes a normalized version of the
    corpus to output. All occurrences in the corpus of terms listed in the output from ``parsed_ontololgy.py`` will have
    its ID appended after a #-sign. Whitespace inside the term will be replaced with underscore.
    """

    def __init__(self, parsed_ontology):
        self.term_to_id = dict()
        self.start_to_rest = dict()
        self.term_freqs = Counter()
        self.analyze_terms(parsed_ontology)

    def analyze_terms(self, parsed_ontlogy):
        pattern = re.compile('[^\w\s]+', re.UNICODE)
        with open(parsed_ontlogy) as po:
            for line in po:
                line = pattern.sub('', line)
                words_to_id = line.strip().lower().split('\t')
                words = words_to_id[0].split()
                self.term_to_id[words_to_id[0]] = words_to_id[1]
                if not words[0] in self.start_to_rest.keys():
                    self.start_to_rest[words[0]] = set()
                if len(words) == 1:
                    self.start_to_rest[words[0]].add('')
                else:
                    self.start_to_rest[words[0]].add(' '.join(words[1:]))

    def spot_terms(self, corpus):
        term_rest = ''
        longest_term = ''
        current_line = ''
        pattern = re.compile('[^\w\s]+', re.UNICODE)
        i = 0
        with open(corpus) as cs:
            for line in cs:
                line = pattern.sub('', line)
                words = line.strip().lower().split()
                while i < len(words):
                    if words[i] in self.start_to_rest.keys():
                        if '' in self.start_to_rest[words[i]]:
                            longest_term = words[i]
                        for j in range(i + 1, len(words)):
                            inside_term = False
                            term_rest += words[j] if len(term_rest) == 0 else ' ' + words[j]
                            for rest in self.start_to_rest[words[i]]:
                                if rest == term_rest:
                                    longest_term = words[i] + ' ' + term_rest
                                if rest.startswith(term_rest + ' '):
                                    inside_term = True
                            if not inside_term:
                                break
                        if longest_term != '':
                            i += len(longest_term.split(' '))
                            longest_term += '#' + self.term_to_id[longest_term]
                            longest_term = longest_term.replace(' ', '_')
                            self.term_freqs[longest_term] += 1
                            current_line += longest_term + ' '
                        else:
                            current_line += words[i] + ' '
                            i += 1
                        term_rest = ''
                        longest_term = ''
                    else:
                        current_line += words[i] + ' '
                        i += 1
                print(current_line.strip())
                current_line = ''
                i = 0

    def print_term_freqs(self):
        with open('term_freqs.tsv', 'w') as tf:
            for (term, freq) in self.term_freqs.most_common():
                tf.write(term + "\t" + str(freq) + "\n")


def main():
    args = docopt("""
    Usage:
        term_spotter.py <parsed_ontology> <corpus>
    """)
    ts = TermSpotter(args['<parsed_ontology>'])
    ts.spot_terms(args['<corpus>'])
    ts.print_term_freqs()


if __name__ == '__main__':
    main()
