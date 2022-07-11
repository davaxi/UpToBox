import re
import csv
import math
import urllib.error
from urllib.request import Request, urlopen


def unhumaize(text):
    powers = {'k': 1, 'm': 2, 'g': 3, 't': 4}

    res = re.match(r'(\d+(?:\.\d+)?)\s?(k|m|g|t)?b?', text, re.IGNORECASE)
    return int(float(res[1]) * math.pow(1024, powers[str(res[2]).lower()]))


def scrap(url):
    match_url = re.findall(r'https:\/\/uptobox\.com\/([a-zA-Z0-9]{12})', url)
    if not match_url:
        print(f'Invalid url : {url}')
        return None

    request = Request(url)
    request.add_header('Referer', 'https://tirexo.io')
    request.add_header('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5')
    try:
        response = urlopen(request).read()
        content = response.decode('utf-8')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f'Not found : {url}')
            return None
        raise e

    match_title = re.findall(r'<title>([^<]+)<\/title>', content, re.MULTILINE)
    if not match_title:
        print(f'Missing title : {url}')
        return None

    match_size = re.findall(r'<h1 class=\'file-title\'>.* \(([^\)]+)\)<\/h1>', content, re.MULTILINE)
    if not match_size:
        print(f'Missing size : {url}')
        return None

    return {
        'token': match_url[0],
        'title': match_title[0],
        'size': unhumaize(match_size[0]),
    }


fieldnames = ['token', 'title', 'size']
with open('data.csv', 'a') as file_csv:
    writer = csv.DictWriter(file_csv, fieldnames=fieldnames)
    # writer.writeheader()
    with open('links.txt', 'r') as file:
        for line in file.readlines():
            data = scrap(line)
            if data:
                writer.writerow(data)
