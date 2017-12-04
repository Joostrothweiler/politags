from flask import Flask
from flask import Response
from redis import Redis

from modules.named_entities.ner import extract_linked_entities


app = Flask(__name__)

@app.route('/')
def hello():
    return 'Home'

@app.route('/ner')
def ner():
    # return 'ner'
    json_ner = extract_linked_entities('En er kwam actie! GroenLinks behaalde weer mooie resultaten bij de begrotingsbehandeling. Hierbij een korte samenvatting.')
    return Response(json_ner)

@app.route('/train')
def train():
    return 'success'

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
