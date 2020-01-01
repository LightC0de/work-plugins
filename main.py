import json
import logging
from collections import namedtuple

import requests
from lxml import html

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M')


def xpath(response, requests):
    return html.fromstring(response.text).xpath(requests)


def get_with_cookies(url):
    json_file = open(NAME_FILE_JSON)
    json_str = json_file.read()
    json_data = json.loads(json_str)

    cookies = dict()
    for e in json_data:
        cookies[e['name']] = e['value']

    s = requests.Session()
    return s.get(url, cookies=cookies)


def post_with_cookies(url, data):
    json_file = open(NAME_FILE_JSON)
    json_str = json_file.read()
    json_data = json.loads(json_str)

    cookies = dict()
    for e in json_data:
        cookies[e['name']] = e['value']

    s = requests.Session()
    return s.post(url, cookies=cookies, data=data)


def get_list_projects(response):
    names = []
    for name in xpath(response, '//a[contains(concat(" ",normalize-space(@class)," ")," visitable ")]'):
        names.append(name.text)

    links = []
    for link in xpath(response, '//a[contains(concat(" ",normalize-space(@class)," ")," visitable ")]/@href'):
        links.append(link)

    i = 0
    projects = []
    while(i < len(names)):
        projects.append({
            'name': names[i],
            'link': links[i],
        })
        i += 1
    return projects


def send_position(url, payload):
    data = {
        'organisation_name': 'Luxoft',
        'key': payload['key'],
        'addOnName': payload['addOnName'],
        'callback': '',
        'licensefieldname': '',
        'referrer': 'pac',
        'binaryURL': payload['binaryURL'],
        'csrfToken': payload['token'],
        'marketplaceTermsConfirm': 'true',
        'marketplaceTerms': 'true',
        'usersubmit': 'true',
        'submit': '',
    }
    return post_with_cookies(url, data)


def get_payload(link):
    try:
        r = get_with_cookies(link)
        token = xpath(r, '//*[@name="csrfToken"]/@value')[0]
        binaryURL = xpath(r, '//*[@name="binaryURL"]/@value')[0]
        addOnName = xpath(r, '//*[@name="addOnName"]/@value')[0]
        key = xpath(r, '//*[@name="key"]/@value')[0]

        return {
            'token': token,
            'binaryURL': binaryURL,
            'addOnName': addOnName,
            'key': key
        }
    except:
        return None


def get_key(payload):
    try:
        r = send_position('https://my.atlassian.com/addon/try', payload)
        return xpath(r, '//*[@id="license-key"]')[0].text
    except:
        return None


def get_links_plugins(file):
    links = []
    with open(file) as f:
        line = f.readline()
        while line:
            links.append(line)
            line = f.readline().rstrip()

    return links


def main():
    global NAME_FILE_JSON
    NAME_FILE_JSON = 'data.json'

    links = get_links_plugins('links.txt')
    keys = dict()
    for link in links:
        payload = get_payload(link)
        if payload != None:
            key = get_key(payload)
        else:
            logging.error(
                'Problem with get key, maybe you need change account!')
            continue

        if key != None:
            keys[payload['addOnName']] = key
            logging.info(f"Added key for: {payload['addOnName']}")
        else:
            logging.error(
                'Problem with get key, maybe you need change account!')
            continue

    if(len(keys) > 0):
        with open("keys.txt", "w+") as f:
            for key, value in keys.items():
                f.write(f'{key}\n{value}\n\n')
        logging.info('Seccusseful writed file with keys!')
    else:
        logging.warning('Array keys is empty!')


if __name__ == "__main__":
    main()
