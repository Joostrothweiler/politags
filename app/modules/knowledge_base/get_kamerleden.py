from lxml import etree
import requests


def get_all_current_members_of_chamber():
    # URL to retrieve all kamerleden
    BASE_URL = 'https://gegevensmagazijn.tweedekamer.nl/OData/v1/'
    URL = BASE_URL + 'Persoon?$filter=Fractielid/any(aa:%20aa/TotEnMet%20eq%20null)&$orderby=Achternaam&$expand=Afbeelding,%20Functie,%20Contactinformatie'
    # Start requests session
    session = requests.session()

    # Use these values to retrieve the data from the XML
    values = ['Titels', 'Initialen', 'Tussenvoegsel', 'Achternaam', 'Voornamen', 'Roepnaam', 'Geslacht',
              'Geboortedatum',
              'Geboorteplaats', 'Geboorteland', 'Overlijdensdatum', 'Overlijdensplaats']
    values_fractielid = ['Functie']
    values_fractie = ['NaamNL', 'Afkorting']

    # Save all data here; this first line contains the column names
    # data = [['id', 'titels', 'initialen', 'tussenvoegsel', 'achternaam', 'voornamen', 'roepnaam', 'geslacht',
    #          'geboortedatum', 'geboorteplaats', 'geboorteland', 'overlijdensdatum', 'overlijdensplaats', 'functie',
    #          'partij_naam', 'partij_afkorting']]
    data = []

    # Specify namespaces, the default namespace has no name, but lxml
    # does not accept empty namespace names so call it 'default' and use
    # 'default' in XPath queries
    ns = {"default": "http://www.w3.org/2005/Atom", "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
          "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"}

    count = 0
    # The API returns max 50 items, so loop over all pages to retrieve all data
    while URL:
        count += 1
        xml = etree.XML(session.get(URL).text.encode('utf-8'))

        for entry in xml.xpath('/default:feed/default:entry', namespaces=ns):
            new_item = []

            # Retrieve the ID of the kamerlid
            person_id = entry.xpath('./default:id/text()', namespaces=ns)[0]
            new_item.append(person_id)

            # Retrieve basic information about this kamerlid
            for entry_property in entry.xpath('./default:content/m:properties', namespaces=ns):
                for value in values:
                    entry_value = entry_property.xpath('./d:' + value + '/text()', namespaces=ns)
                    if entry_value:
                        new_item.append(entry_value[0])
                    else:
                        new_item.append('')

            # Retrieve information about the function within the fractie of
            # this kamerlid
            fractielid_xml = etree.XML(session.get(person_id + '/Fractielid').text.encode('utf-8'))
            # A person can have multiple entries as fractielid, e.g., when
            # they changed parties or when they left their function for a
            # while. We only take the most recent entry for now.
            for entry in fractielid_xml.xpath('//default:content', namespaces=ns)[0]:
                for entry_property in entry.xpath('./m:properties', namespaces=ns):
                    for value in values_fractielid:
                        entry_value = entry_property.xpath('./d:' + value + '/text()', namespaces=ns)
                        if entry_value:
                            new_item.append(entry_value[0])
                        else:
                            new_item.append('')

            fractie_url = BASE_URL + \
                          fractielid_xml.xpath('/default:feed/default:entry/default:link[@title="Fractie"]/@href',
                                               namespaces=ns)[0]
            fractie_xml = etree.XML(session.get(fractie_url).text.encode('utf-8'))

            # Retrieve partij naam and afkorting of kamerlid
            for entry_property in fractie_xml.xpath('//default:content/m:properties', namespaces=ns):
                for value in values_fractie:
                    entry_value = entry_property.xpath('./d:' + value + '/text()', namespaces=ns)
                    if entry_value:
                        new_item.append(entry_value[0])
                    else:
                        new_item.append('')


            if len(new_item[3]) > 1:
                last_name = new_item[3].strip() + ' ' + new_item[4].strip()
            else:
                last_name = new_item[4].strip()

            data.append({
                'system_id': abs(hash(new_item[0])) % (10 ** 8),
                'title': new_item[1].strip(),
                'initials': new_item[2].strip(),
                'last_name': last_name,
                'first_name': new_item[5].strip(),
                'given_name': new_item[6].strip(),
                'role': new_item[12].strip(),
                'party': new_item[14].strip(),
                'municipality': '',
                'suffix': '',
                'department': '',
            })

        # Check if a 'next' URL is provided
        URL = xml.xpath('/default:feed/default:link[@rel="next"]/@href', namespaces=ns)
        if URL:
            URL = URL[0]

    return data
