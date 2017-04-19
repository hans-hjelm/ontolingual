from docopt import docopt
from ontofeature.hyperwd_feature import HyperwdFeature

def main():
    args = docopt("""
    Usage:
        feature_generator.py <path_to_wordlist> <path_to_hyperwords_dir>
    """)
    hwf = HyperwdFeature(args['<path_to_hyperwords_dir>'])


if __name__ == '__main__':
    main()
