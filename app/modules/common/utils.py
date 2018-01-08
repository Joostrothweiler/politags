from difflib import SequenceMatcher

import datetime
from bs4 import BeautifulSoup
from flask import json
from nameparser import HumanName
from nameparser.config import CONSTANTS

CONSTANTS.titles.add('dhr', 'mw', 'drs', 'ing', 'ir', 'jhr', 'jkvr')
CONSTANTS.suffix_acronyms.remove('bart')
CONSTANTS.first_name_titles.remove('van', 'van der', 'van den')

def get_document_identifier(document):
    url = document['meta']['pfl_url']
    identifier = url.split('/')[-1]
    return identifier


def translate_doc(document):
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


def fix_empty_document_fields(document):
    if not 'description' in document:
        document['description'] = 'none'
    if not 'parties' in document:
        document['parties'] = []
    if not 'location' in document:
        document['location'] = 'unknown'
    if not 'collection' in document:
        document['collection'] = 'unknown'

    return document


def html2text(html):
    # TODO: Does not yet successfully handle all html input like &amp;
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text().strip().replace('\n', ' ')
    return text


def parse_human_name(name):
    human_name = HumanName(name)

    return {
        'title': human_name['title'].strip(),
        'first_name': human_name['first'].strip(),
        'last_name': (html2text(human_name['middle'] + ' ' + human_name['last'])).strip(),
        'suffix': human_name['suffix'].strip(),
    }


def collection_as_dict(collection):
    dict_array = []
    for model in collection:
        dict_array.append(model.as_dict())
    return dict_array


def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def pure_len(str):
    return len(str) - str.count(' ')


def timeStamped(fname, fmt='%Y%m%d-%H%M_{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname=fname)
