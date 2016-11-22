# Pymorm
Really simple pymongo-based ODM for MongoDB. The only requirements are Bunch and, obviously, pymongo.

## Updates
 
 * **0.4.9**   Solved bug overwriting False/None values with the default value.
 
 * **0.4.7**   Better explaining errors at index resolution stage.

 * **0.4.6**   Index resolution is not mandatory anymore.

 * **0.4.4**   Fixed manipulator to avoid errors if `None` is returned by a query.
 
 * **0.4.3**   Added missing support to sparse indexes.
 
 * **0.4.2**   Added MongoDB>=3.0 with WiredTiger support.
 
 * **0.4.1**   Added pymongo>=3.0 support. Documentation improved.
 
 * **0.4.0**   General refactoring. Moved everything from `__init__.py`. Changed `.commit()` to `.save()`.
 
 * **0.3.4**   Overwritten default `find_and_modify` behavior, setting `manipulate=True` so that it returns an instance of
           the mapped class instead of a dictionary.
           
 * **0.3.3**   Cleaner mapping for returned documents. No need to monkeypatch the Cursor class anymore.
 
 * **0.3.0**   Added `__defaults__` property in `MongoObject`, used to declare default values for documents.
           The fields in `__defaults__` can also be callable. The callable will be called the first time the document is 
           retrieved through the library.
 

## Example

```
from pymorm import MongoObject, MongoObjectMeta
from pymongo import MongoClient

db = MongoClient("mongodb://localhost:27017/pymorm").get_default_database()


class Test(MongoObject):
    __metaclass__ = MongoObjectMeta
    __collection__ = db.tests

    __defaults__ = {"username": "Test",
                    "happiness": lambda: "poor"}

    def test_method(self, test):
        return test

    @property
    def test_property(self):
        return "test"

    @classmethod
    def test_classmethod(cls):
        return cls.__name__


user = Test.add({})
user2 = Test.add({"username": "Walter"})
user2.happiness = "a lot!"
print user
print user2
user.save()

> User(_id=ObjectId('5519e5eb5dde7310f04d9bbe'), happiness=u'poor', username=u'Test') 
> User(_id=ObjectId('5519e5eb5dde7310f04d9bbe'), happiness=u'a lot!', username=u'Walter') 

```

### Enjoy!
