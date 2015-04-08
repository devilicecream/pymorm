__author__ = 'walter'
from .collection_wrapper import CollectionMethodWrapper


class Query(object):
    def __init__(self, collection):
        self.collection = collection

    def find_and_modify(self, query=None, update=None,
                        upsert=False, sort=None, full_response=False,
                        manipulate=True, **kwargs):

        query = query and query or {}
        return self.collection.find_and_modify(query=query, update=update, upsert=upsert,
                                               sort=sort, full_response=full_response, manipulate=manipulate,
                                               **kwargs)

    def __getattr__(self, item):
        if not hasattr(self, item):
            setattr(self, item, CollectionMethodWrapper(self.collection, item))
        return getattr(self, item)