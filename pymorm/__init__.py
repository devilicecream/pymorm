__author__ = 'walter'
from bunch import *
from pymongo.cursor import Cursor
from pymongo.errors import OperationFailure
from bson import ObjectId

__all__ = ["MongoObject", "MongoObjectMeta"]


class CollectionMethod(object):
    def __init__(self, mappedclass, method):
        self.mappedclass = mappedclass
        self.method = method

    def __call__(self, *args, **kwargs):
        result = self.method(*args, **kwargs)
        if isinstance(result, dict):
            return self.mappedclass(result)
        elif isinstance(result, Cursor):
            # trick to map Cursor.next() on the appropriate mapped class.
            result.next = self.map_cursor(result.next)
        return result

    def map_cursor(self, next):
        def _do_map_cursor():
            return self.mappedclass(next())
        return _do_map_cursor


class Query(object):
    def __init__(self, mappedclass, collection):
        self.mappedclass = mappedclass
        self.collection = collection

    def __getattr__(self, item):
        return CollectionMethod(self.mappedclass, getattr(self.collection, item))


class MongoObjectMeta(type):
    def __new__(mcs, *args, **kwargs):
        result = type(*args)
        result.query = Query(result, result.__collection__)
        return result


class MongoObject(Bunch):
    __defaults__ = {}

    def __init__(self, *args, **kw):
        super(MongoObject, self).__init__(*args, **kw)
        for key, value in self.__defaults__.items():
            if not self.get(key):
                self[key] = hasattr(value, '__call__') and value() or value

    @classmethod
    def add(cls, document):
        new_id = ObjectId(cls.query.insert(document))
        return cls.query.find_one({"_id": new_id})

    @classmethod
    def get_all(cls, *args, **kw):
        return [d for d in cls.query.find(*args, **kw)]

    def commit(self, silent_fail=True):
        print dict(self)
        result = self.__class__.query.update({"_id": self._id}, dict(self))
        if not silent_fail and result.updatedExisting is not True:
            raise OperationFailure("The document to update doesn't exist anymore. "
                                   "Updates to the `_id` field are not allowed through `commit`.")
        return result
