from bs4 import BeautifulSoup
import yaml
import requests
from docset import DocSet, Entry

if __name__ == '__main__':

    indexes = yaml.load(open('indexes.yaml', 'r').read())['cmdlet']

    docset = DocSet('PowerShell')

    for index in indexes:

        page = requests.get(index['url']).content
        soup = BeautifulSoup(page)

        group = index['name']

        for div in soup.find_all('div'):

            try:
                if div['data-toclevel'] == '2':
                    link = div.a.attrs['href'].strip()
                    title = div.a.attrs['title']

                    docset.entries.append(
                        Entry(title, group+'-'+title+'.html', 'Command', link))

            except KeyError:
                pass

    docset.create()
