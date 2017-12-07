from difflib import SequenceMatcher

def get_document_identifier(document):
    url = document['meta']['pfl_url']
    identifier = url.split('/')[-1]
    return identifier


def translate_doc(document):
    simple_doc = {}
    simple_doc['id'] = get_document_identifier(document)
    simple_doc['url'] = 'https://api.poliflw.nl/v0/combined_index/' + get_document_identifier(document)
    simple_doc['description'] = document['description']
    simple_doc['parties'] = document['parties']
    simple_doc['source'] = document['source']
    simple_doc['title'] = document['title']
    simple_doc['type'] = document['type']

    return simple_doc

def collection_as_dict(collection):
    dict_array = []
    for model in collection:
        dict_array.append(model.as_dict())
    return dict_array

def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()
