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


def standardize_party_name(party):
    synonyms = [
        {'synonym': 'Christen Democratisch Appel (CDA)', 'standardized': 'CDA'},
        {'synonym': 'Partij van de Arbeid (P.v.d.A.)', 'standardized': 'PvdA'},
        {'synonym': 'Partij van de Arbeid (P.v.d.A)', 'standardized': 'PvdA'},
        {'synonym': 'Democraten 66 (D66)', 'standardized': 'D66'},
        {'synonym': 'SP (Socialistische Partij)', 'standardized': 'SP'},
        {'synonym': 'Staatkundig Gereformeerde Partij (SGP)', 'standardized': 'SGP'},
        {'synonym': 'GROENLINKS', 'standardized': 'GroenLinks'},
        {'synonym': 'Groenlinks', 'standardized': 'GroenLinks'},
        {'synonym': 'PVV (Partij voor de Vrijheid)', 'standardized': 'PVV'},
        {'synonym': 'GemeenteBelangen', 'standardized': 'Gemeentebelangen'},
        {'synonym': 'Gemeente Belangen', 'standardized': 'Gemeentebelangen'},
        {'synonym': 'Partij Gemeente Belangen', 'standardized': 'Gemeentebelangen'},
        {'synonym': 'Combinatie Gemeentebelangen', 'standardized': 'Gemeentebelangen'},
        {'synonym': 'ChristenUnie/SGP', 'standardized': 'SGP/ChristenUnie'},
        {'synonym': 'ChristenUnie-SGP', 'standardized': 'SGP/ChristenUnie'},
        {'synonym': 'SGP-ChristenUnie', 'standardized': 'SGP/ChristenUnie'},
        {'synonym': 'Christenunie', 'standardized': 'ChristenUnie'},
        {'synonym': 'PVDA/GroenLinks', 'standardized': 'PvdA/GroenLinks'},
        {'synonym': 'PvdA/GROENLINKS', 'standardized': 'PvdA/GroenLinks'},
        {'synonym': 'PvdA-GROENLINKS', 'standardized': 'PvdA/GroenLinks'},
        {'synonym': 'PvdA-Groenlinks', 'standardized': 'PvdA/GroenLinks'},
        {'synonym': 'PvdA-GroenLinks', 'standardized': 'PvdA/GroenLinks'},
        {'synonym': 'Lokale Politieke Federatie Westland', 'standardized': 'LPF Westland'},
        {'synonym': 'GemeenteBelang Westland (GBW)', 'standardized': 'GemeenteBelang Westland'},
        {'synonym': '', 'standardized': ''},
        {'synonym': '', 'standardized': ''},
        {'synonym': '', 'standardized': ''}
    ]

    for obj in synonyms:
        if party == obj['synonym']:
            party = obj['standardized']

    return party


def standardize_gender(gender):
    if gender == 'm':
        return 'male'
    elif gender == 'v':
        return 'female'
    else:
        return 'unknown'


def guess_gender(title):
    titles = title.lower().split(' ')
    male_titles = ['dhr.', 'jhr.', 'mr']
    female_titles = ['mw.']

    if len(list(set(titles) & set(male_titles))) > len(list(set(titles) & set(female_titles))):
        return 'm'
    elif len(list(set(titles) & set(female_titles))) > len(list(set(titles) & set(male_titles))):
        return 'v'
    else:
        return 'unknown'


def get_politicians_from_archive():
    logger.info('Updating knowledge base')
    logger.info('Initializing politicians (and update)')

    data = []
    # Fetch data from almanak and members of chamber chamber
    for person in get_all_current_members_of_chamber():
        data.append(person)

    for person in get_all_current_local_politicians():
        data.append(person)

    for person in get_all_current_ministers():
        data.append(person)

    # Clean data
    candidates = []
    with open('data_resources/politicians/candidates-2018.csv') as csv_file:
        dr = csv.DictReader(csv_file, delimiter=',')
        for candidate in dr:
            candidates.append(candidate)

    for person in data:
        person = clean_politician_data_using_candidates_file(person, candidates)

    save_new_politicians_file(data)
    logger.info('Done')


def save_new_politicians_file(data):
    # Save new politicians file
    with open('data_resources/politicians/politicians_enriched.csv', 'w') as csvfile:
        fieldnames = ['system_id', 'title', 'initials', 'first_name', 'given_name', 'last_name', 'suffix', 'party',
                      'department', 'municipality', 'role', 'gender']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for person in data:
            writer.writerow(person)


def clean_politician_data_using_candidates_file(politician, candidates):
    politician['gender'] = guess_gender(politician['title'])
    for candidate in candidates:
        if candidate['initials'].lower() == politician['initials'].lower() \
                and candidate['last_name'].lower() == politician['last_name'].lower() \
                and candidate['municipality'].lower() == politician['municipality'].lower() \
                and standardize_party_name(candidate['party']).lower() == standardize_party_name(politician['party']).lower():

            politician['given_name'] = candidate['given_name']
            politician['party'] = standardize_party_name(candidate['party'])

            if guess_gender(politician['title']) in ['m', 'v']:
                politician['gender'] = standardize_gender(guess_gender(politician['title']))
            else:
                politician['gender'] = standardize_gender(candidate['gender'])

    return politician
