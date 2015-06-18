__author__ = 'walter'

from pymorm import MongoObject, MongoObjectMeta, Document
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.cursor import Cursor


db = MongoClient("mongodb://localhost:27017/pymorm").get_default_database()


class Test(MongoObject):
    __metaclass__ = MongoObjectMeta
    __collection__ = db.tests
    __indexes__ = [('test', ASCENDING), ('walter', DESCENDING)]
    __unique_indexes__ = [[('test', DESCENDING), ('_id', DESCENDING)]]

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


if __name__ == "__main__":
    assert Test.query.remove({}).__class__ == Document
    user = Test.add({})
    user2 = Test.add({"username": "Walter"})
    user.happiness = "a lot!"
    print user
    print user2
    user.save()
    assert [d for d in Test.query.find({})][0].__class__ == Test
    assert [d for d in Test.query.find({}).skip(1).limit(1)][0].__class__ == Test
    assert next(Test.query.find({}).skip(1).limit(1)). __class__ == Test
    query = Test.query.find({}).skip(1).limit(1).explain()
    assert query.__class__ == Document, query.__class__
    assert Test.get_all({}).__class__ == list
    assert Test.query.find({}).__class__ == Cursor
    assert user.remove() == 1, "Problem with delete"
    result = Test.query.find_and_modify(query={}, update={"$set": {"gianni": 2}})
    assert result.__class__ == Test, result.__class__
    assert len(Test.get_all({})) == 1, "Something went wrong, the number of documents is %s" % len(Test.get_all({}))
