__author__ = 'walter'
from .mapped_manipulator import MappedSONManipulator
from .query import Query
from .document import Document
from bson import ObjectId
from pymongo.errors import OperationFailure
import logging

log = logging.getLogger('pymorm')


class MongoObjectMeta(type):
    """
    Metaclass for the Pymorm mapped classes. It will bind the
    database connection to the class, and add the `MappedSONManipulator`,
    required to return the query results as a mapped class instance (or `Document`)
    instead of a dict.
    It also resolves the indexes as specified in the mapped class properties.
    """
    def __new__(mcs, *args, **kwargs):
        """
        Create the mapped class.
        Set `__collection__.mappedclass` to use it in the `MappedSONManipulator`.
        Adding the `query` property to use it as a collection method wrapper.
        """
        result = type(*args)
        result.__collection__.mappedclass = result
        result.__collection__.database.add_son_manipulator(MappedSONManipulator())
        result.query = Query(result.__collection__)
        try:
            mcs.resolve_indexes(result)
        except Exception as e:
            raise OperationFailure(e)
            # raise OperationFailure("Can not resolve the indexes. ")
        return result

    @classmethod
    def resolve_indexes(mcs, cls):
        """
        Resolve the indexes as stated by the class properties
        `__indexes__` and `__unique_indexes__`.
        The indexes specified in the `__indexes__` array will be created not unique.
        The indexes specified in the `__unique_indexes__` array will be created as unique.
        """
        if cls.__dont_resolve_indexes__ == True:
            return
        # Get existing indexes
        try:
            # Catch OperationFailure raised by MongoDB > 3.0 with WiredTiger if the collection doesn't already exist.
            current_indexes = cls.query.index_information().items()
            existing_indexes = filter(lambda x: not x[1].get('unique') and not x[0] == '_id_',
                                      current_indexes)
            existing_unique_indexes = filter(lambda x: x[1].get('unique'),
                                             current_indexes)
            existing_sparse_indexes = filter(lambda x: x[1].get('sparse'),
                                             current_indexes)
        except OperationFailure:
            existing_indexes = []
            existing_unique_indexes = []
            existing_sparse_indexes = []
        # Normalize indexes
        indexes = [i if hasattr(i[0], '__iter__') else [i] for i in cls.__indexes__]
        unique_indexes = [i if hasattr(i[0], '__iter__') else [i] for i in cls.__unique_indexes__]
        sparse_indexes = [i if hasattr(i[0], '__iter__') else [i] for i in cls.__sparse_indexes__]

        def check_indexes(_indexes, _existing, unique, sparse=False):
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
                cls.query.create_index(new_index, unique=unique, sparse=sparse)

        check_indexes(indexes, existing_indexes, unique=False)
        check_indexes(unique_indexes, existing_unique_indexes, unique=True)
        check_indexes(sparse_indexes, existing_sparse_indexes, unique=True, sparse=True)


class MongoObject(Document):
    """
    Superclass for every mapped class using Pymorm.

    Every subclass must have `MongoObjectMeta` as `__metaclass__`.

    The `__defaults__` attribute is used to give default values to the created documents.
    No schema is enforced using the `__defaults__` attribute.

    The `__indexes__` and `__unique_indexes__` attributes are array of MongoDB indexes,
    specified as ('<index_field>', ASCENDING/DESCENDING) in case of a single index,
    [('<field_one>', ASCENDING/DESCENDING), ('<field_two>', ASCENDING/DESCENDING)] in case
    of a combined index.
    """
    __defaults__ = {}
    __dont_resolve_indexes__ = False
    __indexes__ = []
    __unique_indexes__ = []
    __sparse_indexes__ = []

    def __init__(self, *args, **kw):
        """
        Creates a new instance of the mapped class and assign the default values if
        not already set.
        If a default value is callable, it will call it and assign the return value to
        the field.
        :param args: same as `dict` type.
        :param kw: same as `dict` type.
        :return: A new mappedclass instance.
        """
        super(MongoObject, self).__init__(*args, **kw)
        for key, value in self.__defaults__.items():
            if not self.get(key):
                self[key] = hasattr(value, '__call__') and value() or value

    @classmethod
    def add(cls, document):
        """
        Insert a new document in the database and return it.
        :param document: The document to insert, casting it to a new mapped class instance,
                         to verify it is an usable document, in case the `__init__` method
                         is overridden with some validation.
        :return: The inserted object as a mapped class instance.
        """
        new_id = ObjectId(cls.query.insert(cls(document)))
        return cls.query.find_one({"_id": new_id})

    @classmethod
    def get_all(cls, *args, **kw):
        """
        Returns all the results of a given simple query, avoiding the need to iterate over the Cursor.
        :param args: *args for the collection `find` method
        :param kw: **kw for the collection `find` method
        :return: A list of mapped class instances with the query results.
        """
        cursor = cls.query.find(*args, **kw)
        return [d for d in cursor]

    def remove(self, silent_fail=False):
        """
        Remove the current object from the database. Raise `OperationFailure` if something goes wrong.
        :param silent_fail: If `True`, doesn't raise if the result from MongoDB shows that something went wrong.
                            Default to `False`.
        :return: The number of documents actually removed from the database (should always be 1).
        """
        result = self.__class__.query.remove({"_id": self._id})
        if not result['ok'] and not silent_fail:
            raise OperationFailure("Can not delete the document")
        return result['n']

    def save(self, silent_fail=True):
        """
        Save the local changes to the object into the database.
        Raise `OperationFailure` if something goes wrong or there's no documents in the database with the local
        object `_id` field.
        :param silent_fail: If `True`, doesn't raise if the result from MongoDB shows that something went wrong.
                            Default to `True`.
        :return: The updated document.
        """
        result = self.__class__.query.update({"_id": self._id}, self)
        if result.updatedExisting is not True and not silent_fail:
            raise OperationFailure("The document to update doesn't exist anymore. "
                                   "Updates to the `_id` field are not allowed through `save`.")
        return result

