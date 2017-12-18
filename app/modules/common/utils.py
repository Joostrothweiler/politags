from difflib import SequenceMatcher
from bs4 import BeautifulSoup


def get_document_identifier(document):
    url = document['meta']['pfl_url']
    identifier = url.split('/')[-1]
    return identifier


def translate_doc(document):
    simple_doc = {
        'id': get_document_identifier(document),
        'html_description': document['description'],
        'text_description': html2text(document['description']),
        'parties': document['parties'],
        'location': document['location'],
        'collection': document['meta']['collection']
    }
    return simple_doc


def html2text(html):
    # TODO: Does not yet successfully handle all html input like &amp;
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text().strip().replace('\n', ' ')
    return text


def collection_as_dict(collection):
    dict_array = []
    for model in collection:
        dict_array.append(model.as_dict())
    return dict_array


def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


