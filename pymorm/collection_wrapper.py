__author__ = 'walter'
from .document import Document


class CollectionMethodWrapper(object):
    def __init__(self, collection, method):
        self.collection = collection
        self.method = method

    def __call__(self, *args, **kwargs):
        result = getattr(self.collection, self.method)(*args, **kwargs)
        if type(result) == dict:
            return Document(result)
        return result