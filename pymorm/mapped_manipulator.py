__author__ = 'walter'
from pymongo.son_manipulator import SONManipulator


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