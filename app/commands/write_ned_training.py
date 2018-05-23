import logging
from datetime import datetime
from flask_script import Command

from app.models.models import EntityLinking, Article, Entity
from app.modules.common.utils import translate_doc
from app.modules.enrichment.named_entities.disambiguation import compute_politician_feature_vector, \
    get_candidate_politicians
from app.modules.enrichment.named_entities.disambiguation_features import f_mention_prior, f_candidate_prior
from app.modules.poliflow.fetch import fetch_single_document

logger = logging.getLogger('write_ned_training')


class WriteNedTraining(Command):
    """ Write NED classifier training file. """

    def run(self):
        logger.info('Start processing for NED writing.')
        write_ned_training()


def write_ned_training():
    result = '['
    result_absolute = '['
    FALSE_LABEL = 0
    TRUE_LABEL = 1

    # Fetch only the articles of interest -> those where the initial certainty does not match the updated certainty
    articles = []
    interesting_linkings = EntityLinking.query.filter(
        EntityLinking.initial_certainty != EntityLinking.updated_certainty).all()

    for linking in interesting_linkings:
        linking_article = linking.entity.article
        if linking_article not in articles:
            articles.append(linking.entity.article)

    logger.info(len(articles))

    # Write the feature vectors of the linkings in each article to a training file.
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

            # Add additional (continuous improvement) features to vector
            f_m = f_mention_prior(entity.text, candidate)
            f_c = f_candidate_prior(candidate)
            feature_vector.append(f_m)
            feature_vector.append(f_c)

            # Insert stress test data
            candidates_count = str(len(get_candidate_politicians(entity)))

            # Probability result
            if linking.updated_certainty < linking.initial_certainty:
                feature_vector.append(FALSE_LABEL)
                result += '["' + str(article.id) + '","' + entity.text + '",' + candidates_count + ',"' + candidate.full_name + \
                          '",' + ','.join(str(x) for x in feature_vector) + '],\n'
            if linking.updated_certainty > linking.initial_certainty:
                feature_vector.append(TRUE_LABEL)
                result += '["' + str(article.id) + '","' + entity.text + '",' + candidates_count + ',"' + candidate.full_name + \
                          '",' + ','.join(str(x) for x in feature_vector) + '],\n'

            # Confirmed and rejected results
            if linking.updated_certainty == 0:
                feature_vector.append(FALSE_LABEL)
                result_absolute += '["' + str(article.id) + '","' + entity.text + '",' + candidates_count + ',"' + candidate.full_name + \
                          '",' + ','.join(str(x) for x in feature_vector) + '],\n'
            if linking.updated_certainty == 1:
                feature_vector.append(TRUE_LABEL)
                result_absolute += '["' + str(article.id) + '","' + entity.text + '",' + candidates_count + ',"' + candidate.full_name + \
                          '",' + ','.join(str(x) for x in feature_vector) + '],\n'

    # Remove last \n + comma and add another bracket for json formatting
    result = result[0:-2]
    result += "]"

    result_absolute = result_absolute[0:-2]
    result_absolute += "]"

    # Write data to a training file with the data as identifying string.
    now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    file = open('data_resources/ned/training/ned_db_training_file_{}.json'.format(now), 'w')
    file.write(result)
    file.close()

    file = open('data_resources/ned/training/ned_db_training_file_absolute_{}.json'.format(now), 'w')
    file.write(result_absolute)
    file.close()

    logger.info('Done.')


