from bs4 import BeautifulSoup
import yaml
import requests
import shutil
import os
import sqlite3

indexes = yaml.load(open('indexes.yaml', 'r').read())['cmdlet']

db = sqlite3.connect('PowerShell.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()
try: cur.execute('DROP TABLE searchIndex;')
except: pass

cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

entries = []

for index in indexes:

    page = requests.get(index['url']).content
    soup = BeautifulSoup(page)

    if not os.path.exists('PowerShell.docset/Contents/Resources/Documents/'+index['name']):
        os.mkdir('PowerShell.docset/Contents/Resources/Documents/'+index['name'])

    for div in soup.find_all('div'):

        try:
            if div['data-toclevel'] == '2':
                link = div.a.attrs['href'].strip()
                title = div.a.attrs['title']

                destination = open('PowerShell.docset/Contents/Resources/Documents/'+index['name']+'/'+title+'.html', 'w')
                destination.write(requests.get(link).content)
                destination.close()

                entries.append({
                                'name': title,
                                'group': index['name'],
                                'path': 'PowerShell.docset/Contents/Resources/Documents/'+index['name']+'/'+title+'.html'
                               })

        except KeyError:
            pass

for entry in entries:
    insert = (entry['name'], 'Command', entry['group']+'/'+entry['name']+'.html')
    cur.execute('insert into searchIndex(name, type, path) values (?,?,?)', insert)

db.commit()

for entry in entries:

    source = open(entry['path'], 'r+')

    soup = BeautifulSoup(source.read())

    try:
        soup.find(id='megabladeContainer').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='ux-header').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='isd_print').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='isd_printABook').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='expandCollapseAll').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='leftNav').decompose()
    except AttributeError:
        pass

    try:
        soup.find_all('div', class_='feedbackContainer')[0].decompose()
    except AttributeError:
        pass
    except IndexError:
        pass

    try:
        soup.find_all('div', class_='communityContentContainer')[0].decompose()
    except AttributeError:
        pass
    except IndexError:
        pass

    try:
        soup.find(id='ux-footer').decompose()
    except AttributeError:
        pass

    for link in soup.find_all('a'):
        for entry in entries:
            if entry['name'] == link.get_text():
                link.attrs['href'] = '../' + entry['group']+'/'+entry['name']+'.html'

    source.seek(0)
    source.write(str(soup))
    source.truncate()
    source.close()
