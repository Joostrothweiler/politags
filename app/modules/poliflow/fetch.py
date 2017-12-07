import requests
import json

def fetch_data(size = 10):
    # Read from the api
    url_string = 'https://api.poliflw.nl/v0/search?size={}'.format(size)
    request = requests.get(url_string, auth=('poliflw', '57p8InibSe.|cwW57P6{+,9_Q'))
    json_response = json.loads(request.text)
    # Return the array of article items
    return json_response['item']


def fetch_latest_article_identifiers(size = 10):
    # Fetch article array
    articles = fetch_data(size)
    # Fetch the identifiers from these articles
    identifiers = []
    for doc in articles:
        identifiers.append(doc['meta']['pfl_url'])

    return identifiers
