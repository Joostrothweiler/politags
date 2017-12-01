from flask import Flask
from flask import Response
from redis import Redis

from modules.named_entities.ner import extract_linked_entities


app = Flask(__name__)
redis = Redis(host='redis', port=6379)

@app.route('/')
def hello():
    count = redis.incr('hits')
    redis.incr('hits')
    return 'Hello World from Docker! I have been seen {} times.\n'.format(count)


@app.route('/ner')
def ner():
    json_ner = extract_linked_entities('En er kwam actie! GroenLinks behaalde weer mooie resultaten bij de begrotingsbehandeling. Hierbij een korte samenvatting.')
    return Response(json_ner)

@app.route('/train')
def train():
    return 'success'

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
