import xml.etree.ElementTree
import csv
import urllib.request
import numpy as np

from flask_script import Command


class ConstructKbCommand(Command):
    """ Construct the database."""

    def run(self):
        download_archive()
        politicians = get_politicians()
        parties = get_parties_from_politicians(politicians)

        write_objects_array_to_file('archive_politicians', ['id', 'name', 'party', 'contact_city'], politicians)
        write_objects_array_to_file('archive_parties', ['name'], parties)

def full_branch_name(branch):
    return '{http://almanak.overheid.nl/schema/export/2.0}' + branch


def download_archive():
    urllib.request.urlretrieve('https://almanak.overheid.nl/archive/exportOO.xml', 'data_resources/archive_export00.xml')


def write_objects_array_to_file(filename, header, array):
    with open('data_resources/{}.csv'.format(filename), 'w') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

        for obj in array:
            writer.writerow(obj)


def get_politicians():
    root = xml.etree.ElementTree.parse('data_resources/archive_export00.xml').getroot()
    politicians = []

    for employee in root.iter(tag=full_branch_name('medewerker')):
        identifier = getattr(employee.find(full_branch_name('systemId'))
                             .find(full_branch_name('systemId')), 'text', '')
        name = getattr(employee.find(full_branch_name('naam')), 'text', '')
        party = getattr(employee.find(full_branch_name('partij')), 'text', '')
        city = getattr(employee.find(full_branch_name('contact'))
                       .find(full_branch_name('postAdres'))
                       .find(full_branch_name('adres'))
                       .find(full_branch_name('plaats')), 'text', '')

        person = {
            'id': identifier,
            'name': name,
            'party': party,
            'contact_city': city
        }
        politicians.append(person)

    return politicians

def get_parties_from_politicians(politicians):
    parties = []

    for politician in politicians:
        party = {
            'name': politician['party']
        }
        if party not in parties:
            parties.append(party)

    return parties