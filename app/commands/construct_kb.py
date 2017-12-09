import xml.etree.ElementTree

from flask_script import Command


class ConstructKbCommand(Command):
    """ Construct the database."""

    def run(self):
        construct_kb()

def construct_kb():
    root = xml.etree.ElementTree.parse('data_resources/archive.xml').getroot()

    # Loop over all organisations
    for org in root.iter(tag=branch_path('organisatie')):
        for item in org:
            if item.attrib and \
                    item.attrib[branch_path('naam')] and \
                    item.attrib[branch_path('naam')] == 'Staten-Generaal':

                    party = org

                    name = getattr(party.find(branch_path('naam')), 'text', '--')
                    abbr = getattr(party.find(branch_path('afkorting')), 'text', '--')
                    desc = getattr(party.find(branch_path('beschrijving')), 'text', '--')

                    print('naam: {}, afkorting: {}, beschrijving: {}'.format(name, abbr, desc))


def branch_path(branch):
    return '{http://almanak.overheid.nl/schema/export/2.0}' + branch