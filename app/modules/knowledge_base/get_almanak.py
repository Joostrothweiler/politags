from lxml import etree
import re
import requests


def get_all_current_ministers():
    # Download and save data, data lake style
    r = requests.get('https://almanak.overheid.nl/archive/exportOO.xml', verify=False)
    xml = etree.XML(r.text)

    # Process ministers and staatssecretarissen
    ministers = []
    for ministerie in xml.xpath(
            '/p:overheidsorganisaties/p:organisaties/p:organisatie/p:categorie[@p:naam="Ministeries"]/..',
            namespaces=xml.nsmap):
        ministerie_naam = ministerie.xpath('p:naam/text()', namespaces=xml.nsmap)[0]
        for functie in ministerie.xpath('.//p:categorie[@p:naam="Ministeries"]/../p:functies/p:functie',
                                        namespaces=xml.nsmap):
            functie_naam = functie.xpath('p:naam/text()', namespaces=xml.nsmap)[0]
            if re.match(r'^Minister.*', functie_naam, re.I) or re.match(r'^Staats.*', functie_naam, re.I):
                # Sometimes wrongly multiple medewerkers are provided, so
                # far the last one has always been the actual one in office
                medewerker_id = \
                    functie.xpath('p:medewerkers/p:medewerker/p:systemId/p:systemId/text()', namespaces=xml.nsmap)[-1]
                medewerker_naam = functie.xpath('p:medewerkers/p:medewerker/p:naam/text()', namespaces=xml.nsmap)[-1]
                ministers.append({
                    'system_id': medewerker_id,
                    'full_name': medewerker_naam,
                    'department': ministerie_naam,
                    'role': functie_naam
                })

    return ministers


def get_all_current_local_politicians():
    # Download and save data, data lake style
    r = requests.get('https://almanak.overheid.nl/archive/exportOO.xml', verify=False)
    xml = etree.XML(r.text)

    # Process gemeentemedewerkers
    gemeentemedewerkers = []

    for gemeente in xml.xpath('/p:overheidsorganisaties/p:gemeenten/p:gemeente', namespaces=xml.nsmap):
        gemeente_naam = gemeente.xpath('./p:naam/text()', namespaces=xml.nsmap)[0]
        gemeente_afkorting = gemeente.xpath('./p:afkorting/text()', namespaces=xml.nsmap)
        # Not every gemeente has an afkorting
        if gemeente_afkorting:
            gemeente_afkorting = gemeente_afkorting[0]
        else:
            gemeente_afkorting = ''
        for functie in gemeente.xpath('./p:functies/p:functie', namespaces=xml.nsmap):
            functie_naam = functie.xpath('p:naam/text()', namespaces=xml.nsmap)[0]
            for medewerker in functie.xpath('./p:medewerkers/p:medewerker', namespaces=xml.nsmap):
                medewerker_id = medewerker.xpath('./p:systemId/p:systemId/text()', namespaces=xml.nsmap)[-1]
                medewerker_naam = medewerker.xpath('./p:naam/text()', namespaces=xml.nsmap)[-1]
                medewerker_partij = medewerker.xpath('./p:partij/text()', namespaces=xml.nsmap)
                # Not every medewerker belongs to a political party
                if medewerker_partij:
                    medewerker_partij = medewerker_partij[0]
                else:
                    medewerker_partij = ''

                gemeentemedewerkers.append({
                    'system_id': medewerker_id,
                    'full_name': medewerker_naam,
                    'party': medewerker_partij,
                    'municipality': gemeente_afkorting,
                    'role': functie_naam,
                })

    return gemeentemedewerkers
