import csv
import logging

from flask_script import Command

from app.modules.common.utils import parse_human_name, write_objects_to_file
from app.modules.knowledge_base.get_almanak import get_all_current_local_politicians, get_all_current_ministers
from app.modules.knowledge_base.get_kamerleden import get_all_current_members_of_chamber

logger = logging.getLogger('construct_kb')


class ConstructKbCommand(Command):
    """ Construct the database."""

    def run(self):
        get_politicians_from_archive()


def get_politicians_from_archive():
    logger.info('Updating knowledge base')
    logger.info('Initializing politicians (and update)')

    data = []

    for person in get_all_current_members_of_chamber():
        data.append(person)

    for person in get_all_current_local_politicians():
        data.append(person)

    for person in get_all_current_ministers():
        data.append(person)

    with open('data_resources/politicians/politicians.csv', 'w') as csvfile:
        fieldnames = ['system_id', 'title', 'initials', 'first_name', 'given_name', 'last_name', 'suffix', 'party', 'department', 'municipality', 'role']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for person in data:
            writer.writerow(person)

    logger.info('done')