__author__ = 'walter'
from bunch import *
from pymongo.errors import OperationFailure
from pymongo.son_manipulator import SONManipulator
from bson import ObjectId
import logging

log = logging.getLogger('pymorm')

__all__ = ["MongoObject", "MongoObjectMeta", "Document"]


class MappedSONManipulator(SONManipulator):
    """Mapped SON Manipulator.

    Will convert the outgoing SON to a <mappedclass> object
    """
    def will_copy(self):
        return False

    def transform_outgoing(self, son, collection):
        """Manipulate an outgoing SON object.

        :Parameters:
          - `son`: the SON object being retrieved from the database
          - `collection`: the collection this object was stored in
        """
        if not isinstance(collection.mappedclass, collection.__class__) and hasattr(son, '_id'):
            return collection.mappedclass(son)
        return son


class CollectionMethod(object):
    def __init__(self, collection, method):
        self.collection = collection
        self.method = method

    def __call__(self, *args, **kwargs):
        result = getattr(self.collection, self.method)(*args, **kwargs)
        if type(result) == dict:
            return Document(result)
        return result


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
        return CollectionMethod(self.collection, item)


class Document(Bunch):
    pass


class MongoObjectMeta(type):
    def __new__(mcs, *args, **kwargs):
        result = type(*args)
        result.__collection__.mappedclass = result
        result.__collection__.database.connection.document_class = Document
        result.__collection__.database.add_son_manipulator(MappedSONManipulator())
        result.query = Query(result.__collection__)
        try:
            mcs.resolve_indexes(result)
        except Exception as e:
            log.error(e)
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


class MongoObject(Document):
    __defaults__ = {}
    __indexes__ = []
    __unique_indexes__ = []

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
        cursor = cls.query.find(*args, **kw)
        return [d for d in cursor]

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
