import csv
import hashlib
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from nameparser import HumanName
from nameparser.config import CONSTANTS as NAME_PARSER_CONSTANTS

NAME_PARSER_CONSTANTS.titles.add('dhr', 'mw', 'drs', 'ing', 'ir', 'jhr', 'jkvr')
NAME_PARSER_CONSTANTS.suffix_acronyms.remove('bart')
NAME_PARSER_CONSTANTS.first_name_titles.remove('van', 'van der', 'van den')


def get_document_identifier(document: dict) -> str:
    """
    Get the document identifier (id) from the poliflow article.
    :param document: The document as found in poliflow.
    :return: Document identifier (id) as string.
    """
    if '_id' in document['meta']:
        identifier = document['meta']['_id']
    else:
        url = document['meta']['pfl_url']
        identifier = url.split('/')[-1]
    return identifier


def translate_doc(document: dict) -> dict:
    """
    Translate the poliflow document into one that we prefer to use. Also works as an interface.
    :param document: The document as found in poliflow.
    :return: A simple document that we use so that this always has the same preprocessed fields.
    """
    document = fix_empty_document_fields(document)
    simple_doc = {
        'id': get_document_identifier(document),
        'html_description': document['description'],
        'text_description': html2text(document['description']),
        'parties': document['parties'],
        'location': document['location'],
        'collection': document['meta']['collection']
    }
    return simple_doc


def fix_empty_document_fields(document: dict) -> dict:
    """
    Overwrite the empty fields with processable ones (if any) in the original document.
    :param document: The document as found in poliflow.
    :return: The same document but with processable fields in the dict.
    """
    if not 'description' in document:
        document['description'] = 'none'
    if not 'parties' in document:
        document['parties'] = []
    if not 'location' in document:
        document['location'] = 'unknown'
    if not 'collection' in document:
        document['collection'] = 'unknown'

    return document


def html2text(html: str) -> float:
    """
    Process the html and transform it to standard text without html tags or weird symbols.
    :param html: The html as string.
    :return: The parsed html as text without any html tags.
    """
    # TODO: Does not yet successfully handle all html input like &amp;
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text().strip().replace('\n', ' ')
    return text


def parse_human_name(name: str) -> dict:
    """
    Parse a name string to a dict based on the HumanName library.
    :param name: String that contains the name.
    :return: Dictionary containing the title, first name, last name, and suffix.
    """
    human_name = HumanName(name)

    return {
        'title': human_name['title'].strip(),
        'first_name': human_name['first'].strip(),
        'last_name': str((html2text(human_name['middle'] + ' ' + human_name['last']))).strip(),
        'suffix': human_name['suffix'].strip(),
    }


def collection_as_dict(collection) -> list:
    """
    Transform a model collection into an array that can be returned through the API.
    :param collection: A model collection from SQLAlchemy.
    :return: Array of model objects included in this collection.
    """
    dict_array = []
    for model in collection:
        dict_array.append(model.as_dict())
    return dict_array


def string_similarity(a: str, b: str) -> float:
    """
    Compute a similarity score between two strings in the range of [0,1].
    :param a: First string to compare
    :param b: Second string to compare
    :return: Similarity score in the range of [0,1]
    """
    return SequenceMatcher(None, a, b).ratio()


def pure_len(a: str) -> int:
    """
    Compute the pure length of characters contained in a string (length without white space).
    :param a: String from which we compute the pure length.
    :return: Pure length of the string (no white space).
    """
    return len(a) - a.count(' ')


def entity_text_has_valid_length(entity) -> bool:
    """
    Check whether the entity has a valid entity.text length such that we can insert it in the database.
    :param entity: NLP entity processed by Spacy.
    :return: Boolean whether entity has valid text length.
    """
    if entity and entity.text:
        return pure_len(entity.text) > 2 and len(entity.text) < 50
    return False


def write_objects_to_file(filename: str, header: list, object_list: list):
    """
    Write an objects list to a csv file with headers.
    :param filename: Name of the file in the folder data_resources to write to.
    :param header: a list containing the header names, should be the same length as the objects in the object_list
    :param object_list: list of objects written to csv file.
    """
    with open('data_resources/{}.csv'.format(filename), 'w') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

        for obj in object_list:
            writer.writerow(obj)


def string2numeric_hash(text):
    text = text.encode('utf-8')
    return int(hashlib.md5(text).hexdigest()[:5], 16)
