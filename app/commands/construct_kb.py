import csv
from flask_script import Command

from app.modules.common.utils import html2text, parse_human_name


class ConstructKbCommand(Command):
    """ Construct the database."""

    def run(self):
        politicians = get_politicians_from_archive_scraper()
        write_objects_to_file('archive_politicians',
                              ['id', 'title', 'first_name', 'last_name', 'suffix', 'party', 'municipality', 'role'], politicians)


def get_politicians_from_archive_scraper():
    politicians = []

    with open('data_resources/archive_scraped.csv') as csv_file:
        data_rows = csv.DictReader(csv_file, delimiter=',')
        for row in data_rows:
            system_id = get_system_id_from_url(row['Address'])
            human_name = parse_human_name(row['Naam'])

            person = {
                'id': system_id,
                'title': human_name['title'],
                'first_name': human_name['first_name'],
                'last_name': human_name['last_name'],
                'suffix': human_name['suffix'],
                'party': row['partij-abbr 1'],
                'municipality': row['gemeente 1'],
                'role': row['functie 1']
            }
            politicians.append(person)

    return politicians


def get_system_id_from_url(url):
    arr = url.split('/')  # ['https:', '', 'almanak.overheid.nl', '126360', 'Mw_D_Dekker-Mulder', '']
    system_id = arr[-3]  # '126360'
    return system_id


def write_objects_to_file(filename, header, array):
    with open('data_resources/{}.csv'.format(filename), 'w') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

        for obj in array:
            writer.writerow(obj)