from flask_script import Command

from app.models.models import EntityLinking, Article, Entity
from app.modules.common.utils import translate_doc
from app.modules.entities.disambiguation import compute_politician_feature_vector, compute_politician_certainty
from app.modules.poliflow.fetch import fetch_single_document


class WriteNedTraining(Command):
    """ Test the NER/NED."""

    def run(self):
        write_ned_training()


def write_ned_training():
    CERTAINTY_BOUNDARY_FALSE_LABEL = 0.2
    CERTAINTY_BOUNDARY_TRUE_LABEL = 0.95
    FALSE_LABEL = 0
    TRUE_LABEL = 1

    # Process per article.
    articles = Article.query.limit(10).all()
    result = ''

    for article in articles:
        # Fetch document from poliflow
        api_document = fetch_single_document(article.id)
        simple_doc = translate_doc(api_document)

        # loop over all linkings
        entities = Entity.query.filter(Entity.article == article).filter(Entity.label == 'PER').all()
        entity_ids = [e.id for e in entities]
        article_entity_linkings = EntityLinking.query.filter(EntityLinking.entity_id.in_(entity_ids)).all()
        # for each linking, create a feature vector
        for linking in article_entity_linkings:
            doc_entities = article.entities
            entity = linking.entity
            candidate = linking.linkable_object

            feature_vector = compute_politician_feature_vector(simple_doc, doc_entities, entity, candidate)
            certainty = compute_politician_certainty(feature_vector)

            if certainty < CERTAINTY_BOUNDARY_FALSE_LABEL:
                feature_vector.append(FALSE_LABEL)
                result += ",".join(str(x) for x in feature_vector) + '\n'
            if certainty > CERTAINTY_BOUNDARY_TRUE_LABEL:
                feature_vector.append(TRUE_LABEL)
                result += ",".join(str(x) for x in feature_vector) + '\n'

    file = open('data_resources/ned_db_training_file.txt', 'w')
    file.write(result)
    file.close()

    print("NED TRAINING: Done.")
