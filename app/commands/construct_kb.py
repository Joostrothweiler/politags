import csv

from app.modules.common.utils import html2text

from flask_script import Command

class ConstructKbCommand(Command):
    """ Construct the database."""

    def run(self):
        # download_archive()
        # politicians = get_politicians_from_archive_export()
        politicians = get_politicians_from_archive_scraper()
        write_objects_array_to_file('archive_politicians', ['id', 'first_name', 'last_name', 'party', 'municipality', 'role'], politicians)


def get_politicians_from_archive_scraper():
    politicians = []

    with open('data_resources/archive_scraped.csv') as csv_file:
        data_rows = csv.DictReader(csv_file, delimiter=',')
        for row in data_rows:
            first_name, last_name = split_name(row['Naam'])
            identifier = get_identifier_from_url(row['Address'])

            person = {
                'id': identifier,
                'first_name': first_name,
                'last_name': last_name,
                'party': row['partij-abbr 1'],
                'municipality': row['gemeente 1'],
                'role': row['functie 1']
            }
            politicians.append(person)

    return politicians


def write_objects_array_to_file(filename, header, array):
    with open('data_resources/{}.csv'.format(filename), 'w') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

        for obj in array:
            writer.writerow(obj)


def split_name(name):
    # Handle html characters such as &amp;
    clean_name = html2text(name)
    # Split to handle first and last name
    arr = clean_name.split('.')
    # If the name ends with a dot, remove the last (empty) entry from array
    if arr[-1] == '':
        del(arr[-1])
    # Get the first and last names from the array
    first_name = ' '.join(arr[:-1])
    last_name = arr[-1].lstrip()

    return first_name, last_name


def get_identifier_from_url(url):
    arr = url.split('/') # ['https:', '', 'almanak.overheid.nl', '126360', 'Mw_D_Dekker-Mulder', '']
    system_id = arr[-3] # '126360'
    return system_id