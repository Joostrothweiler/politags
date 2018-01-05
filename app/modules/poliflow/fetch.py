import requests
import json

from app.local_settings import PFL_USER, PFL_PASSWORD


def fetch_data(size):
    documents = []
    per_page = 100
    offset = 0
    # Paginated fetch
    while len(documents) < size:
        # Read from the api
        url_string = 'https://api.poliflw.nl/v0/search?size={}&from={}'.format(per_page, offset)
        request = requests.get(url_string, auth=(PFL_USER, PFL_PASSWORD))
        json_response = json.loads(request.text)
        # Return the array of document items
        items = json_response['item']
        for item in items:
            if len(documents) < size:
                documents.append(item)

        offset += per_page

    return documents

def fetch_latest_documents(size = 1000):
    # Fetch document array
    documents = fetch_data(size)
    return documents