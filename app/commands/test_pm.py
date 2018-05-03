import logging
from flask_script import Command, Option

import nl_core_news_sm

from app.models.models import Politician, Party
from app.modules.common.utils import translate_doc
from app.modules.enrichment.named_entities.recognition import init_nlp
from app.modules.poliflow.fetch import fetch_latest_documents

logger = logging.getLogger('test_pm')
nlp = None

class TestPhraseMatcherCommand(Command):
    """ Test the NER/NED."""
    option_list = (
        Option('--count', '-c', dest='count'),
    )

    def run(self, count = 100):
        test_phrase_matcher(int(count))


def test_phrase_matcher(count):
    """ Test Named Entity Algorithms."""
    # Fetch the articles
    logger.info('Fetching {} artilces'.format(count))
    n_documents = count
    documents = fetch_latest_documents(n_documents)
    logger.info('Fetched {} articles'.format(len(documents)))

    # Process the descriptions to raw text (instead of html)
    document_descriptions = []
    for document in documents:
        simple_doc = translate_doc(document)
        document_descriptions.append(simple_doc['text_description'])

    # Process the articles using two different NLP modules. With and without phrase matcher.
    logger.info('Initializing nlp model')
    nlp_original = nl_core_news_sm.load()
    nlp_with_phrase_matcher = init_nlp()
    logger.info(nlp_with_phrase_matcher)

    logger.info('Processing article descriptions')
    nlp_original_extracted_entities = []
    nlp_with_phrase_matcher_extracted_entities = []

    for doc_description in document_descriptions:
        for ent in nlp_original(doc_description).ents:
            nlp_original_extracted_entities.append(ent)

        for ent in nlp_with_phrase_matcher(doc_description).ents:
            nlp_with_phrase_matcher_extracted_entities.append(ent)

    exact_politician_name_matches(nlp_with_phrase_matcher_extracted_entities, nlp_original_extracted_entities)
    initial_politician_name_matches(nlp_with_phrase_matcher_extracted_entities, nlp_original_extracted_entities)
    full_party_name_matches(nlp_with_phrase_matcher_extracted_entities, nlp_original_extracted_entities)
    abbreviation_party_name_matches(nlp_with_phrase_matcher_extracted_entities, nlp_original_extracted_entities)
    count_types_recognized(nlp_with_phrase_matcher_extracted_entities, nlp_original_extracted_entities)


def exact_politician_name_matches(entities_with, entities_without):
    with_count = 0
    for entity in entities_with:
        if entity.label_ == 'PER':
            if Politician.query.filter(Politician.first_last == entity.text).first():
                with_count += 1

    without_count = 0
    for entity in entities_without:
        if entity.label_ == 'PER':
            if Politician.query.filter(Politician.first_last == entity.text).first():
                without_count += 1

    logger.info('exact_politician_name_matches with PhraseMatcher: {}'.format(with_count))
    logger.info('exact_politician_name_matches NO PhraseMatcher: {}'.format(without_count))

def initial_politician_name_matches(entities_with, entities_without):
    with_count = 0
    for entity in entities_with:
        if entity.label_ == 'PER':
            if Politician.query.filter(Politician.full_name_short == entity.text).first():
                with_count += 1

    without_count = 0
    for entity in entities_without:
        if entity.label_ == 'PER':
            if Politician.query.filter(Politician.full_name_short == entity.text).first():
                without_count += 1

    logger.info('initial_politician_name_matches with PhraseMatcher: {}'.format(with_count))
    logger.info('initial_politician_name_matches NO PhraseMatcher: {}'.format(without_count))

def full_party_name_matches(entities_with, entities_without):
    with_count = 0
    for entity in entities_with:
        if entity.label_ == 'ORG':
            if Party.query.filter(Party.name == entity.text).first():
                with_count += 1

    without_count = 0
    for entity in entities_without:
        if entity.label_ == 'ORG':
            if Party.query.filter(Party.name == entity.text).first():
                without_count += 1

    logger.info('full_party_name_matches with PhraseMatcher: {}'.format(with_count))
    logger.info('full_party_name_matches NO PhraseMatcher: {}'.format(without_count))

def abbreviation_party_name_matches(entities_with, entities_without):
    with_count = 0
    for entity in entities_with:
        if entity.label_ == 'ORG':
            if Party.query.filter(Party.abbreviation == entity.text).first():
                with_count += 1

    without_count = 0
    for entity in entities_without:
        if entity.label_ == 'ORG':
            if Party.query.filter(Party.abbreviation == entity.text).first():
                without_count += 1

    logger.info('abbreviation_party_name_matches with PhraseMatcher: {}'.format(with_count))
    logger.info('abbreviation_party_name_matches NO PhraseMatcher: {}'.format(without_count))

def count_types_recognized(entities_with, entities_without):
    with_count_people = 0
    with_count_organizations = 0

    for entity in entities_with:
        if entity.label_ == 'PER':
            with_count_people += 1
        elif entity.label_ == 'ORG':
            with_count_organizations += 1

    without_count_people = 0
    without_count_organizations = 0

    for entity in entities_without:
        if entity.label_ == 'PER':
            without_count_people += 1
        elif entity.label_ == 'ORG':
            without_count_organizations += 1

    logger.info('count_types_recognized PER matches with PhraseMatcher: {}'.format(with_count_people))
    logger.info('count_types_recognized PER matches NO PhraseMatcher: {}'.format(without_count_people))

    logger.info('count_types_recognized ORG matches with PhraseMatcher: {}'.format(with_count_organizations))
    logger.info('count_types_recognized ORG matches NO PhraseMatcher: {}'.format(without_count_organizations))