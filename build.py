from bs4 import BeautifulSoup
import yaml
import requests
import sqlite3
import timeit

class DocSet(object):

    def __init__(self, name):

        self.name = name
        self.init_db()
        self.entries = []

    @property
    def path(self):

        return '{name}.docset'.format(name = self.name)

    def init_db(self):

        path = '{path}/Contents/Resources/docSet.dsidx'.format(path = self.path)

        database = sqlite3.connect(path)

        cursor = database.cursor()

        try: cursor.execute('DROP TABLE searchIndex;')
        except: pass

        cursor.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        cursor.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

        database.commit()
        database.close()

    def insert_entries(self):

        path = '{path}/Contents/Resources/docSet.dsidx'.format(path = self.path)

        database = sqlite3.connect(path)

        cursor = database.cursor()

        inserts = [(entry.name, entry.type_, entry.path) for entry in self.entries]

        cursor.executemany('insert into searchIndex(name, type, path) values (?,?,?)', inserts)

        database.commit()
        database.close()

    def create(self):

        for entry in list(self.entries):
            try:
                entry.download()
                print 'Downloaded {entry}'.format(entry = entry.name)
            except Exception, e:
                print 'Failed to download {entry}'.format(entry = entry.name)
                print str(e)
                self.entries.remove(entry)

        for entry in self.entries: entry.rewrite(self.entries)
        self.insert_entries()

class Entry(object):

    def __init__(self, name, path, type_, url, docset):

        self.name = name
        self.type_ = type_
        self.url = url
        self.docset = docset
        self.path = path

    @property
    def full_path(self):

        return '{docset}/Contents/Resources/Documents/{path}'.format(
                                                    docset = self.docset.path,
                                                    path = self.path)

    def download(self):

        r = requests.get(self.url)

        if r.status_code == 200:

            with open(self.full_path, 'w') as f:

                f.write(r.content)

        else:

            raise Exception('Received "{code}" when downloading "{name}"'.format(
                                                        code = r.status_code,
                                                        name = self.name))

    def rewrite(self, entries):

        source = open(self.full_path, 'r+')

        soup = BeautifulSoup(source.read())

        unnecessary = [
            '#megabladeContainer',
            '#ux-header',
            '#isd_print',
            '#isd_printABook',
            '#expandCollapseAll',
            '#leftNav',
            '.feedbackContainer',
            '#isd_printABook',
            '.communityContentContainer',
            '#ux-footer'
        ]

        for u in unnecessary:

            if u[0] == '#':

                try:
                    soup.find(id=u[1:]).decompose()
                except AttributeError:
                    pass

            elif u[0] == '.':

                for element in soup.find_all('div', class_=u[1:]):
                    element.decompose()

        for link in soup.find_all('a'):
            for entry in entries:
                try:
                    if link.attrs['href'] == entry.url:
                        link.attrs['href'] = entry.path
                except KeyError:
                    pass

        source.seek(0)
        source.write(str(soup))
        source.truncate()
        source.close()

        print 'Finished rewriting {entry}'.format(entry = self.name)

if __name__ == '__main__':

    start = timeit.default_timer()

    indexes = yaml.load(open('indexes.yaml', 'r').read())['cmdlet']

    docset = DocSet('PowerShell')

    for index in indexes:

        r = requests.get(index['url'])

        if r.status_code == 200:

            soup = BeautifulSoup(r.content)
            group = index['name']

            for div in soup.find_all('div'):

                try:
                    if div['data-toclevel'] == '2':
                        link = div.a.attrs['href'].strip()
                        title = div.a.attrs['title']

                        docset.entries.append(
                            Entry(title, group+'-'+title+'.html', 'Command', link, docset))

                except KeyError:
                    pass

            print 'Finished indexing {index}'.format(index = index['name'])

        else:

            print 'Failed to index {index} ({code})'.format(
                                        index = index['name'],
                                        code = r.status_code)

    docset.create()

    stop = timeit.default_timer()

    print 'Downloaded {count} entries in {elapsed} seconds.'.format(
                                                count = len(docset.entries),
                                                elapsed = (stop - start))
