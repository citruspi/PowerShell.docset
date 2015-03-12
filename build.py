from bs4 import BeautifulSoup
import yaml
import requests
from docset import DocSet, Entry

indexes = yaml.load(open('indexes.yaml', 'r').read())['cmdlet']

docset = DocSet('PowerShell')

entries = []

for index in indexes:

    page = requests.get(index['url']).content
    soup = BeautifulSoup(page)

    for div in soup.find_all('div'):

        try:
            if div['data-toclevel'] == '2':
                link = div.a.attrs['href'].strip()
                title = div.a.attrs['title']

                entries.append(
                    Entry(title, index['name']+'-'+title+'.html', 'Command', link, docset))

        except KeyError:
            pass

for entry in entries: entry.download()

docset.insert_entries(entries)

for entry in entries: entry.rewrite(entries)
