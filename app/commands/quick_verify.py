import logging
import re

from flask_script import Command

from app import db

from app.models.models import EntityLinking, Verification, Article
from app.modules.common.utils import translate_doc
from app.modules.computation.questioning import process_entity_verification, generate_questions
from app.modules.poliflow.fetch import fetch_single_document

logger = logging.getLogger('quick_verify')


class QuickVerifyCommand(Command):
    """ Initialize the database."""

    def run(self):
        quick_verify()



def quick_verify():
    for article in Article.query.all():
        document = fetch_single_document(article.id)
        simple_doc = translate_doc(document)
        simple_doc['cookie_id'] = 'TERMINAL'
        question_api_response = generate_questions(simple_doc, simple_doc['cookie_id'])

        if 'error' in question_api_response:
            print(question_api_response['error'])

        if 'error' not in question_api_response and question_api_response['label'] == 'PER':
            print(simple_doc['text_description'] + '\n')

            entity_linking_id = question_api_response['question_linking_id']
            entity_linking = EntityLinking.query.filter(EntityLinking.id == entity_linking_id).first()

            entity = entity_linking.entity
            politician = entity_linking.linkable_object


            print('Entity : \t{} from {} - {}'.format(entity.text, simple_doc['location'], simple_doc['parties']))
            print('Politician: \t{} ({}) {} of {} from {}'.format(politician.title, politician.first_name, politician.full_name, politician.party, politician.municipality))

            response = input("Is this correct? [y,n,?,stop]: ")
            response_str = str(response)

            apidoc = simple_doc

            if response_str == 'y':
                print('You said yes.')
                apidoc['response_id'] = politician.id
                process_entity_verification(entity_linking_id, apidoc)
            elif response_str == 'n':
                print('You said no.')
                apidoc['response_id'] = -1
                process_entity_verification(entity_linking_id, apidoc)
            elif response_str == 'stop':
                print('You want to stop.')
                return
            else:
                print('You probably meant that you do not know. Lets continue.')
            print('\n\n')
    print('Thanks!')