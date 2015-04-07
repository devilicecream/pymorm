# Pymorm
Really simple pymongo-based ORM for MongoDB. The only requirements are Bunch and, obviously, pymongo.

# Updates

 * **0.3.0**   Added `__defaults__` property in `MongoObject`, used to declare default values for documents.
           The fields in `__defaults__` can also be callable. The callable will be called the first time the document is 
           retrieved through the library.
 
 * **0.3.3**   Cleaner mapping for returned documents. No need to monkeypatch the Cursor class anymore.
 * **0.3.4**   Overwritten default `find_and_modify` behavior, setting `manipulate=True` so that it returns an instance of
           the mapped class instead of a dictionary.

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
user.commit()

> User(_id=ObjectId('5519e5eb5dde7310f04d9bbe'), happiness=u'poor', username=u'Test') 
> User(_id=ObjectId('5519e5eb5dde7310f04d9bbe'), happiness=u'a lot!', username=u'Walter') 

```

### Enjoy!
