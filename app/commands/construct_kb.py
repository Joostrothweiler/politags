import xml.etree.ElementTree
import csv
import urllib.request
import wikipedia

from flask_script import Command


class ConstructKbCommand(Command):
    """ Construct the database."""

    def run(self):
        download_archive()
        politicians = get_politicians()
        write_objects_array_to_file('archive_politicians', ['id', 'first_name', 'last_name', 'party', 'contact_city'], politicians)


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

        first_name, last_name = split_name(name)

        person = {
            'id': identifier,
            'first_name': first_name,
            'last_name': last_name,
            'party': party,
            'contact_city': city
        }

        if not person in politicians and not person['first_name'] == '' and len(person['last_name']) > 1:
            politicians.append(person)


    return politicians


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

def split_name(name):
    splitted = name.split('.')
    first_name = ' '.join(splitted[:-1])
    last_name = splitted[-1].lstrip()

    return first_name, last_name