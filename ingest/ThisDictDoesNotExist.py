class ThisDictDoesNotExist(object):
    def __getitem__(self, item):
        return self

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return True
