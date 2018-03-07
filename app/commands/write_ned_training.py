import logging
from datetime import datetime
from flask_script import Command

from app.models.models import EntityLinking, Article, Entity
from app.modules.common.utils import translate_doc
from app.modules.enrichment.named_entities.disambiguation import compute_politician_feature_vector
from app.modules.poliflow.fetch import fetch_single_document

logger = logging.getLogger('write_ned_training')


class WriteNedTraining(Command):
    """ Write NED classifier training file. """

    def run(self):
        logger.info('Start processing for NED writing.')
        write_ned_training()


def write_ned_training():
    result = ''
    FALSE_LABEL = 0
    TRUE_LABEL = 1

    articles = []
    interesting_linkings = EntityLinking.query.filter(not EntityLinking.initial_certainty == EntityLinking.updated_certainty).all()
    for linking in interesting_linkings:
        linking_article = linking.entity.article
        if linking_article not in articles:
            articles.append(linking.entity.article)

    for article in articles:
        # Fetch document from poliflow
        api_document = fetch_single_document(article.id)
        simple_doc = translate_doc(api_document)
        # loop over all linkings
        doc_entities = article.entities
        doc_entities_people = Entity.query.filter(Entity.article == article).filter(Entity.label == 'PER').all()
        entity_ids = [e.id for e in doc_entities_people]
        article_entity_linkings = EntityLinking.query.filter(EntityLinking.entity_id.in_(entity_ids)).all()
        # for each linking, create a feature vector
        for linking in article_entity_linkings:
            entity = linking.entity
            candidate = linking.linkable_object
            feature_vector = compute_politician_feature_vector(simple_doc, doc_entities, entity, candidate)

            if linking.updated_certainty < linking.initial_certainty:
                feature_vector.append(FALSE_LABEL)
                result += str(article.id) + ',' + entity.text + ',' + candidate.full_name + ',' + ','.join(
                    str(x) for x in feature_vector) + '\n'
            if linking.updated_certainty > linking.initial_certainty:
                feature_vector.append(TRUE_LABEL)
                result += str(article.id) + ',' + entity.text + ',' + candidate.full_name + ',' + ','.join(
                    str(x) for x in feature_vector) + '\n'

    now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    file = open('data_resources/ned/training/ned_db_training_file_{}.txt'.format(now), 'w')
    file.write(result)
    file.close()

    logger.info('Done.')
