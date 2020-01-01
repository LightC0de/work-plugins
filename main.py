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
    r = get_with_cookies(link)

    token = xpath(r, '//*[@name="csrfToken"]/@value')[0]
    binaryURL = xpath(r, '//*[@name="binaryURL"]/@value')[0]
    addOnName = xpath(r, '//*[@name="addOnName"]/@value')[0]
    key = xpath(r, '//*[@name="key"]/@value')[0]

    print('addOnName', addOnName)

    return {
        'token': token,
        'binaryURL': binaryURL,
        'addOnName': addOnName,
        'key': key,
    }


def get_key(payload):
    r = send_position('https://my.atlassian.com/addon/try', payload)
    return xpath(r, '//*[@id="license-key"]')[0].text


def main():
    global NAME_FILE_JSON
    NAME_FILE_JSON = 'data.json'

    # Получение данных их формы
    link = 'https://my.atlassian.com/addon/try/com.greffon.folio?referrer=pac&binaryURL=https%3A%2F%2Fmarketplace.atlassian.com%2Fdownload%2Fapps%2F1211259%2Fversion%2F1300360'
    payload = get_payload(link)

    # Отправление post запроса на получение ключа
    key = get_key(payload)
    print(key)


if __name__ == "__main__":
    main()
