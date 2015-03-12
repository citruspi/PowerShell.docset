import sqlite3

class DocSet(object):

    def __init__(self, name):

        self.name = name
        self.init_db()

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

    def insert_entries(self, entries):

        path = '{path}/Contents/Resources/docSet.dsidx'.format(path = self.path)

        database = sqlite3.connect(path)

        cursor = database.cursor()

        inserts = []

        for e in entries:

            inserts.append(
                (e['name'], 'Command', e['group']+'/'+e['name']+'.html'))

        cursor.executemany('insert into searchIndex(name, type, path) values (?,?,?)', inserts)

        database.commit()
        database.close()

class Entry(object):

    def __init__(self, name, type_, url, docset):

        self.name = name
        self.type_ = type_
        self.url = url
        self.docset = docset

    @property
    def path(self):

        return '{name}.html'.format(name = self.name)

    @property
    def full_path(self):

        return '{docset}.docset/Contents/Resources/Documents/{name}.html'.format(
                                                    docset = self.docset.name,
                                                    name = self.name)

    def download(self):

        r = requests.get(link)

        if r.status_code == 200:

            with open(self.full_path, 'w') as f:

                f.write(r.content)

        else:

            raise Exception('Received "{code}" when downloading "{name}"'.format(
                                                        code = r.status_code,
                                                        name = self.name))
