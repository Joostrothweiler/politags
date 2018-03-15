from lxml import etree
import re
import requests
import logging

logger = logging.getLogger('get_almanak')

from app.modules.common.utils import parse_human_name


def get_all_current_ministers():
    # Download and save data, data lake style
    r = requests.get('https://almanak.overheid.nl/archive/exportOO.xml', verify=False)
    xml = etree.XML(r.text)

    # Process politicians and staatssecretarissen
    politicians = []
    for ministerie in xml.xpath(
            '/p:overheidsorganisaties/p:organisaties/p:organisatie/p:categorie[@p:naam="Ministeries"]/..',
            namespaces=xml.nsmap):
        department = ministerie.xpath('p:naam/text()', namespaces=xml.nsmap)[0]
        for role in ministerie.xpath('.//p:categorie[@p:naam="Ministeries"]/../p:functies/p:functie',
                                        namespaces=xml.nsmap):
            role_name = role.xpath('p:naam/text()', namespaces=xml.nsmap)[0]
            if re.match(r'^Minister.*', role_name, re.I) or re.match(r'^Staats.*', role_name, re.I):
                # Sometimes wrongly multiple medewerkers are provided, so
                # far the last one has always been the actual one in office
                system_id = \
                    role.xpath('p:medewerkers/p:medewerker/p:systemId/p:systemId/text()', namespaces=xml.nsmap)[-1]
                politician_name = role.xpath('p:medewerkers/p:medewerker/p:naam/text()', namespaces=xml.nsmap)[-1]


                human_name = parse_human_name(politician_name)
                last_name = human_name['last_name'].encode('latin1').decode('utf8')
                politicians.append({
                    'system_id': system_id.strip(),
                    'title': human_name['title'].strip(),
                    'initials': human_name['first_name'].strip(),
                    'last_name': last_name.strip(),
                    'suffix': human_name['suffix'].strip(),
                    'role': role_name.strip(),
                    'department': department.strip(),
                    'first_name': '',
                    'party': '',
                    'municipality': '',
                    'given_name': '',
                })

    return politicians


def get_all_current_local_politicians():
    # Download and save data, data lake style
    r = requests.get('https://almanak.overheid.nl/archive/exportOO.xml', verify=False)
    xml = etree.XML(r.text)

    # Process politicians
    politicians = []

    for municipality in xml.xpath('/p:overheidsorganisaties/p:gemeenten/p:gemeente', namespaces=xml.nsmap):
        municipality_name = municipality.xpath('./p:naam/text()', namespaces=xml.nsmap)[0]
        municipality_abbreviation = municipality.xpath('./p:afkorting/text()', namespaces=xml.nsmap)
        # Not every gemeente has an afkorting
        if municipality_abbreviation:
            municipality_abbreviation = municipality_abbreviation[0]
        else:
            municipality_abbreviation = ''
        for role in municipality.xpath('./p:functies/p:functie', namespaces=xml.nsmap):
            role_name = role.xpath('p:naam/text()', namespaces=xml.nsmap)[0]
            for politician in role.xpath('./p:medewerkers/p:medewerker', namespaces=xml.nsmap):
                system_id = politician.xpath('./p:systemId/p:systemId/text()', namespaces=xml.nsmap)[-1]
                full_name = politician.xpath('./p:naam/text()', namespaces=xml.nsmap)[-1].encode('utf-8')
                party = politician.xpath('./p:partij/text()', namespaces=xml.nsmap)
                # Not every medewerker belongs to a political party
                if party:
                    party = party[0]
                else:
                    party = ''

                human_name = parse_human_name(full_name)
                last_name = human_name['last_name'].encode('latin1').decode('utf8')
                politicians.append({
                    'system_id': system_id.strip(),
                    'title': human_name['title'].strip(),
                    'first_name': '',
                    'initials': human_name['first_name'].strip(),
                    'last_name': last_name.strip(),
                    'suffix': human_name['suffix'].strip(),
                    'party': party.strip(),
                    'municipality': municipality_abbreviation.strip(),
                    'role': role_name.strip(),
                    'given_name': '',
                    'department': '',
                })

    return politicians
