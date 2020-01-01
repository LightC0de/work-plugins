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


def send_position(url, csrfToken):
    try:
        r = get_with_cookies(url)
        print(xpath(r, '//*[@name="csrfToken"]/@value')[0])
        data = {
            'organisation_name': 'Putto',
            'key': 'com.onresolve.jira.groovy.groovyrunner.data-center',
            'addOnName': 'ScriptRunner for Jira Data Center',
            'callback': '',
            'licensefieldname': '',
            'referrer': 'pac',
            'binaryURL': 'https://marketplace.atlassian.com/download/apps/6820/version/1002340',
            'csrfToken': csrfToken,
            'marketplaceTermsConfirm': 'true',
            'marketplaceTerms': 'true',
            'usersubmit': 'true',
            'submit': '',
        }
    except:
        logging.error('Problem this project..')
        data = {}
    return post_with_cookies(url, data)


def main():
    global NAME_FILE_JSON
    NAME_FILE_JSON = 'data.json'

    # Получение csrfToken
    link = 'https://my.atlassian.com/addon/try/com.onresolve.jira.groovy.groovyrunner.data-center?referrer=pac&binaryURL=https%3A%2F%2Fmarketplace.atlassian.com%2Fdownload%2Fapps%2F6820%2Fversion%2F1002340'
    r = get_with_cookies(link)
    token = xpath(r, '//*[@name="csrfToken"]/@value')[0]
    print(xpath(r, '//title')[0].text)
    print(token)
    
    # Отправление post запроса на получение ключа
    r = send_position('https://my.atlassian.com/addon/try', token)
    print(r.text)


if __name__ == "__main__":
    main()
