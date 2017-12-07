from difflib import SequenceMatcher
import html2text

def get_document_identifier(document):
    url = document['meta']['pfl_url']
    identifier = url.split('/')[-1]
    return identifier


def translate_doc(document):
    simple_doc = {}
    simple_doc['id'] = get_document_identifier(document)
    simple_doc['html_description'] = document['description']
    simple_doc['text_description'] = html2text.html2text(document['description'])

    return simple_doc

def collection_as_dict(collection):
    dict_array = []
    for model in collection:
        dict_array.append(model.as_dict())
    return dict_array

def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()
