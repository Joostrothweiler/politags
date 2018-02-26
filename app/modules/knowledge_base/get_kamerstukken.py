#!/usr/bin/env python

import sys
import re
import datetime
import json

from bs4 import BeautifulSoup
import requests

import logging

logger = logging.getLogger('blaat')
# logger.setLevel(level=logging.INFO)

caps = "([A-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"


def remove_unnecessary_spaces(sentence):
    return re.sub(' +', ' ', sentence).strip()


def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    if "Ph.D" in text: text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub("\s" + caps + "[.] ", " \\1<prd> ", text)
    text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(caps + "[.]" + caps + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    text = re.sub(" " + caps + "[.]", " \\1<prd>", text)
    if "”" in text: text = text.replace(".”", "”.")
    if "\"" in text: text = text.replace(".\"", "\".")
    if "!" in text: text = text.replace("!\"", "\"!")
    if "?" in text: text = text.replace("?\"", "\"?")
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [remove_unnecessary_spaces(s) for s in sentences]
    return sentences


def fetch_ao_url(url):
    try:
        request = requests.get(url, verify=False)
        status_code = request.status_code
        content = request.content
    except requests.ConnectionError:
        status_code = -1
        content = u''
    except requests.HTTPError:
        status_code = -2
        content = u''
    except requests.URLRequired:
        status_code = -3
        content = u''
    except requests.TooManyRedirects:
        status_code = -4
        content = u''
    except requests.HTTPError:
        status_code = -5
        content = u''
    except requests.RequestException:
        status_code = -6
        content = u''
    return status_code, content


def find_kamerstukken(content, url, what, saved_kamerstukken_urls):
    urls = []
    soup = BeautifulSoup(content, "lxml")

    try:
        lijst = soup.findAll('div', 'lijst')[0]
    except IndexError:
        lijst = None

    if lijst is None:
        return [], []

    kamerstukken = []
    for a in lijst.findAll('a'):
        if what == 'ao':
            match = re.match('\/(kst)-([^\.]*?)\.html', a['href'])
        else:
            match = re.match('\/(kv|ah)-([^\.]*?)\.html', a['href'])
        if match:
            new = 'https://zoek.officielebekendmakingen.nl/%s-%s.html' % (match.group(1), match.group(2),)
            if new not in saved_kamerstukken_urls:
                kamerstukken.append(new)

    try:
        paginering = soup.findAll('div', 'paginering beneden')[0]
    except IndexError:
        paginering = None

    if paginering is None:
        return kamerstukken, []

    max_count = paginering.findAll('a')[-2].findAll(text=True)

    if max_count[0] == 'Vorige' or int(max_count[0]) <= 0:
        return kamerstukken, []

    try:
        last_page = int(max_count[0])
    except ValueError:
        last_page = 0

    urls = []
    cur_page = 1
    while (cur_page <= last_page):
        next_page = cur_page + 1
        new_url = re.sub('&_page=(\d+)', '', url)
        new_url += '&_page=%s' % (next_page,)
        cur_page = next_page
        urls.append(new_url)
    # urls = [a['href'] for a in paginering.findAll('a')]

    print(len(urls))

    return kamerstukken, urls


def find_category_and_text_from_kamerstuk_url(kamerstuk_url):
    statuscode, content = fetch_ao_url(kamerstuk_url)
    soup = BeautifulSoup(content, "lxml")

    meta = soup.find('meta', attrs={'name': 'OVERHEID.category'})
    if meta:
        category = meta['content']
    else:
        category = 'NOCAT'

    content = soup.find("div", {"id": "broodtekst"})
    if content:
        content_html = content.get_text()
    else:
        content_html = 'NOCONTENT'

    sentences = split_into_sentences(content_html)
    content = ' '.join(sentences)

    return category, content


def write_results_to_json(result):
    with open('data_resources/topics/kamerstukken/kamerstukken_topics.json', 'w') as outfile:
        json.dump(result, outfile)


def get_already_saved_kamerstukken():
    file = 'data_resources/topics/kamerstukken/kamerstukken_topics.json'
    data = json.load(open(file))
    return data


def main(args):
    days_in_month = {
        '01': '31',
        '02': '28',
        '03': '31',
        '04': '30',
        '05': '31',
        '06': '30',
        '07': '31',
        '08': '31',
        '09': '30',
        '10': '31',
        '11': '30',
        '12': '31',
    }

    what_to_par = {
        'ao': 'Kamerstuk',
        'kamervragen': (
            'Aanhangsel+van+de+Handelingen%7cKamervragen+zonder+antwoord')
    }

    what_to_vrt = {
        'ao': 'vrt=Verslag+van+een+algemeen+overleg&zkd=AlleenInDeTitel&',
        'kamervragen': ''
    }
    all_kamerstukken_urls = []
    saved_kamerstukken = get_already_saved_kamerstukken()
    saved_kamerstukken_urls = [kamerstuk['url'] for kamerstuk in saved_kamerstukken]

    # year = int(args[0])
    # week = int(args[1])
    # datum_start = isoweek_to_date(year, week)
    # datumstart = datum_start.strftime('%Y%m%d')
    # datum_eind = (datum_start + datetime.timedelta(days=6))
    # datumeind = datum_eind.strftime('%Y%m%d')
    datum_start = datetime.datetime.strptime(args[0], '%Y%m%d')
    datum_eind = datetime.datetime.strptime(args[1], '%Y%m%d')
    days_between = int(args[3])

    datum_curr = datum_start
    while (datum_curr < datum_eind):
        datumstart = datum_curr.strftime('%Y%m%d')
        datum_weekeind = datum_curr + datetime.timedelta(days=days_between)
        datumeind = datum_weekeind.strftime('%Y%m%d')
        par = what_to_par[args[2]]
        zoek = what_to_vrt[args[2]]
        url = (
                'https://zoek.officielebekendmakingen.nl/zoeken/resultaat/'
                '?zkt=Uitgebreid&pst=ParlementaireDocumenten&' + zoek +
                'dpr=AnderePeriode&spd=' + datumstart + '&epd=' + datumeind +
                '&kmr=TweedeKamerderStatenGeneraal&sdt=KenmerkendeDatum&par=' +
                par + '&dst=Opgemaakt%7cOpgemaakt+na+onopgemaakt&isp=true&pnr=1&'
                      'rpp=10&_page=1&sorttype=1&sortorder=4')
        status_code, content = fetch_ao_url(url)
        logger.info('%s: %s' % (url, status_code,))

        if status_code != 200:
            return

        kamerstukken, urls = find_kamerstukken(content, url, args[2], saved_kamerstukken_urls)
        all_kamerstukken_urls += kamerstukken

        for url in urls:
            status_code, content = fetch_ao_url(url)
            # print url, status_code

            if status_code != 200:
                continue

            kamerstukken, dummy = find_kamerstukken(content, url, args[2], saved_kamerstukken_urls)
            all_kamerstukken_urls += kamerstukken

        datum_curr = datum_curr + datetime.timedelta(days=(days_between + 1))

    all_kamerstukken_urls_clean = list(set(all_kamerstukken_urls))

    for kamerstuk_url in all_kamerstukken_urls_clean:
        category, content = find_category_and_text_from_kamerstuk_url(kamerstuk_url)
        saved_kamerstukken.append({'url': kamerstuk_url, 'category': category, 'content': content})

    print(len(saved_kamerstukken))
    write_results_to_json(saved_kamerstukken)


if __name__ == '__main__':
    # ./bin/zoek_ob.py 20150101 20150201 kamervragen 1
    main(sys.argv[1:])
