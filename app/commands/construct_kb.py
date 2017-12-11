import xml.etree.ElementTree
import csv
import urllib.request

from flask_script import Command


class ConstructKbCommand(Command):
    """ Construct the database."""

    def run(self):
        download_archive()
        politicians = get_politicians()
        write_objects_array_to_file('archive_politicians', politicians)


def full_branch_name(branch):
    return '{http://almanak.overheid.nl/schema/export/2.0}' + branch


def download_archive():
    urllib.request.urlretrieve('https://almanak.overheid.nl/archive/exportOO.xml', 'data_resources/archive_export00.xml')


def write_objects_array_to_file(filename, array):
    with open('data_resources/{}.csv'.format(filename), 'w') as file:
        fieldnames = ['id', 'name', 'party', 'contact_city']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
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

# def construct_kb():
#     root = xml.etree.ElementTree.parse('data_resources/archive.xml').getroot()
#
#     # Loop over all organisations
#     for org in root.iter(tag=full_branch_name('organisatie')):
#         for item in org:
#             if item.attrib and \
#                     item.attrib[full_branch_name('naam')] and \
#                     item.attrib[full_branch_name('naam')] == 'Staten-Generaal':
#                 party = org
#
#                 name = getattr(party.find(full_branch_name('naam')), 'text', '--')
#                 abbr = getattr(party.find(full_branch_name('afkorting')), 'text', '--')
#                 desc = getattr(party.find(full_branch_name('beschrijving')), 'text', '--')
#
#                 print('naam: {}, afkorting: {}, beschrijving: {}'.format(name, abbr, desc))
