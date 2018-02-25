import logging
import re

from flask_script import Command

from app import db

from app.models.models import EntityLinking, Verification
from app.modules.common.utils import translate_doc
from app.modules.computation.questioning import process_entity_verification
from app.modules.poliflow.fetch import fetch_single_document

logger = logging.getLogger('quick_verify')


class QuickVerifyCommand(Command):
    """ Initialize the database."""

    def run(self):
        quick_verify()



def quick_verify():
    for current_entity_linking in EntityLinking.query.filter(EntityLinking.linkable_type == 'Politician').filter(
            EntityLinking.initial_certainty == EntityLinking.updated_certainty).all():

        entity = current_entity_linking.entity
        politician = current_entity_linking.linkable_object
        article = entity.article
        document = fetch_single_document(article.id)
        simple_doc = translate_doc(document)

        print(simple_doc['text_description'] + '\n')
        print('Entity : \t{} from {} - {}'.format(entity.text, simple_doc['location'], simple_doc['parties']))
        print('Politician: \t{} ({}) {} of {} from {}'.format(politician.title, politician.first_name, politician.full_name, politician.party, politician.municipality))

        response = input("Is this correct? [y,n,?,stop]: ")
        response_str = str(response)

        apidoc = simple_doc
        apidoc['cookie_id'] = 'TERMINAL'

        if response_str == 'y':
            print('You said yes.')
            apidoc['response_id'] = politician.id
            process_entity_verification(current_entity_linking.id, apidoc)
        elif response_str == 'n':
            print('You said no.')
            apidoc['response_id'] = -1
            process_entity_verification(current_entity_linking.id, apidoc)
        elif response_str == 'stop':
            print('You want to stop.')
            return
        else:
            print('You probably meant that you do not know. Lets continue.')
        print('\n\n')
    print('Thanks!')