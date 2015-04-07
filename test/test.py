__author__ = 'walter'

from pymorm import MongoObject, MongoObjectMeta, Document
from pymongo import MongoClient, ASCENDING, DESCENDING


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

try:
    user = Test.add({})
    user2 = Test.add({"username": "Walter"})
    user.happiness = "a lot!"
    print user
    print user2
    user.commit()
    assert [d for d in Test.query.find({})][0].__class__ == Test
    assert [d for d in Test.query.find({}).skip(1).limit(1)][0].__class__ == Test
    assert next(Test.query.find({}).skip(1).limit(1)). __class__ == Test
    assert Test.query.find({}).skip(1).limit(1).explain().__class__ == Document
    assert user.remove() == 1, "Problem with delete"
    result = Test.query.find_and_modify(query={}, update={"$set": {"gianni": 2}})
    assert result.__class__ == Test
    assert len(Test.get_all({})) == 1, "Something went wrong, the number of documents is %s" % len(Test.get_all({}))
finally:
    assert Test.query.remove({}).__class__ == Document
