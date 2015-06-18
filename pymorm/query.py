__author__ = 'walter'
from .document import Document


class CollectionMethodProxy(object):
    """
    A proxy for the collection methods.
    """
    def __init__(self, collection, method):
        self.collection = collection
        self.method = method

    def __call__(self, *args, **kwargs):
        """
        The actual proxy for the collection methods.
        Also checks if a method returned a `dict`, and converts it to a `Document`
        :param args: The proxied *args
        :param kwargs: The proxied **kwargs
        :return: The result of the proxied method
        """
        result = getattr(self.collection, self.method)(*args, **kwargs)
        if type(result) == dict:
            return Document(result)
        return result


class Query(object):
    """
    Wrapper around the collection. Uses `CollectionMethodWrapper` as
    a proxy to the native (pymongo) collection methods.
    """
    def __init__(self, collection):
        self.collection = collection

    def find_and_modify(self, query=None, update=None,
                        upsert=False, sort=None, full_response=False,
                        manipulate=True, **kwargs):
        """
        Overriding `find_and_modify` to use `manipulate=True` as default instead of the
        pymongo default value of `manipulate=False'.
        Enables the result to be manipulated, thus returning an instance of mapped class
        instead of a `dict`.
        """
        query = query or {}
        return self.collection.find_and_modify(query=query, update=update, upsert=upsert,
                                               sort=sort, full_response=full_response, manipulate=manipulate,
                                               **kwargs)

    def __getattr__(self, item):
        """
        Creates the proxies around the collection methods and stores them to be reused,
        instead of recreating the object every time.
        """
        if not hasattr(self, item):
            setattr(self, item, CollectionMethodProxy(self.collection, item))
        return getattr(self, item)
