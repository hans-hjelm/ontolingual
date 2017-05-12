from docopt import docopt
import xml.etree.ElementTree as ET


def main():
    args = docopt("""
    Usage:
        parse_ontology.py <path_to_xml_file>
    """)
    parse_ontology(args['<path_to_xml_file>'])


def parse_ontology(path_to_xml_file):
    tree = ET.parse(path_to_xml_file)
    root = tree.getroot()
    for record in root.findall('RECORD'):
        libelle = record.find('LIBELLE').text.lower()
        descripteur_id = record.find('DESCRIPTEUR_ID').text.lower()
        if 'translation' in libelle:
            continue
        print(libelle, descripteur_id, sep='\t', end='\n')


if __name__ == '__main__':
    main()
