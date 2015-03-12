class DocSet(object):

    def __init__(self, name):

        self.name = name

    @property
    def path(self):

        return '{name}.docset'.format(name = self.name)
