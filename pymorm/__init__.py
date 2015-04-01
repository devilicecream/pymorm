__author__ = 'walter'
from bunch import *
from pymongo.cursor import Cursor
from pymongo.errors import OperationFailure
from bson import ObjectId
import logging

log = logging.getLogger('pymorm')

__all__ = ["MongoObject", "MongoObjectMeta"]


class CollectionMethod(object):
    def __init__(self, mappedclass, method, debug=False):
        self.mappedclass = mappedclass
        self.method = method
        self.debug = debug

    def log_query(self, cursor, query, parameters):
        explain = cursor.explain()
        msg = "%s - Query: %s.%s%s Query parameters: %s" % (explain['cursor'], self.method.im_self.name,
                                                            self.method.__name__, query, parameters)
        if 'Basic' in explain['cursor']:
            log.warning(msg)
        else:
            log.debug(msg)

    def __call__(self, *args, **kwargs):
        result = self.method(*args, **kwargs)
        if isinstance(result, dict) and result.get('_id'):
            return self.mappedclass(result)
        elif isinstance(result, Cursor):
            if self.debug:
                self.log_query(result, args, kwargs)
            # trick to map Cursor.next() on the appropriate mapped class.
            result.next = self.map_cursor(result.next)
        return result

    def map_cursor(self, next):
        def _do_map_cursor():
            return self.mappedclass(next())
        return _do_map_cursor


class Query(object):
    def __init__(self, mappedclass, collection, debug):
        self.mappedclass = mappedclass
        self.collection = collection
        self.debug = debug

    def __getattr__(self, item):
        return CollectionMethod(self.mappedclass, getattr(self.collection, item), self.debug)


class MongoObjectMeta(type):
    def __new__(mcs, *args, **kwargs):
        result = type(*args)
        result.query = Query(result, result.__collection__, result.__debug_queries__)
        try:
            mcs.resolve_indexes(result)
        except:
            raise OperationFailure("Can not resolve the indexes. ")
        return result

    @classmethod
    def resolve_indexes(mcs, cls):
        existing_indexes = filter(lambda x: not x[1].get('unique') and not x[0] == '_id_',
                                  cls.query.index_information().items())
        existing_unique_indexes = filter(lambda x: x[1].get('unique'),
                                         cls.query.index_information().items())
        # Normalize indexes
        indexes = [i if hasattr(i[0], '__iter__') else [i] for i in cls.__indexes__]
        unique_indexes = [i if hasattr(i[0], '__iter__') else [i] for i in cls.__unique_indexes__]

        def check_indexes(_indexes, _existing, unique):
            for index in _existing:
                key = index[1]['key']
                if key in _indexes:
                    # Existing index
                    _indexes.remove(key)
                else:
                    # Stray index
                    cls.query.drop_index(index[0])
            for new_index in _indexes:
                # New index
                cls.query.create_index(new_index, unique=unique)

        check_indexes(indexes, existing_indexes, unique=False)
        check_indexes(unique_indexes, existing_unique_indexes, unique=True)


class MongoObject(Bunch):
    __defaults__ = {}
    __indexes__ = []
    __unique_indexes__ = []
    __debug_queries__ = False

    def __init__(self, *args, **kw):
        super(MongoObject, self).__init__(*args, **kw)
        for key, value in self.__defaults__.items():
            if not self.get(key):
                self[key] = hasattr(value, '__call__') and value() or value

    @classmethod
    def add(cls, document):
        new_id = ObjectId(cls.query.insert(cls(document)))
        return cls.query.find_one({"_id": new_id})

    @classmethod
    def get_all(cls, *args, **kw):
        return [d for d in cls.query.find(*args, **kw)]

    def remove(self):
        result = self.__class__.query.remove({"_id": self._id})
        if not result['ok']:
            raise OperationFailure("Can not delete the document")
        return result['n']

    def commit(self, silent_fail=True):
        result = self.__class__.query.update({"_id": self._id}, self)
        if not silent_fail and result.updatedExisting is not True:
            raise OperationFailure("The document to update doesn't exist anymore. "
                                   "Updates to the `_id` field are not allowed through `commit`.")
        return result
