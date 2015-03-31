# Pymorm
Really simple pymongo-based ORM for MongoDB. The only requirements are Bunch and, obviously, pymongo.

## Example

```
from pymorm import MongoObject, MongoObjectMeta
from pymongo import MongoClient

db = MongoClient("mongodb://localhost:27017/pymorm").get_default_database()

class User(MongoObject):
    __metaclass__ = MongoObjectMeta
    __collection__ = db.users
    
user = User.add({"username": "Walter"})
user.happiness = "a lot!"
user.commit()

print User.query.find_one()

> User(_id=ObjectId('5519e5eb5dde7310f04d9bbe'), happiness=u'a lot!', username=u'Walter') 

```

# Enjoy!
