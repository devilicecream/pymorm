__author__ = 'walter'
from pymongo.son_manipulator import SONManipulator
from .document import Document


class MappedSONManipulator(SONManipulator):
    """Mapped SON Manipulator.

    Will convert the outgoing SON to a <mappedclass> object
    """
    def transform_outgoing(self, son, collection):
        """Manipulate an outgoing SON object.
        This is actually the method that will manipulate the outgoing data.
        In case the returned document is not an actual collection document
        (for example in the case of a `remove` or `explain, the document will be
        converted from `dict` to `Document`, so that the user can access its fields
        with the dotted notation.

        :Parameters:
          - `son`: the SON object being retrieved from the database
          - `collection`: the collection this object was stored in
        """
        if son is None:
            return son
        if not isinstance(collection.mappedclass, collection.__class__) and son.get('_id'):
            return collection.mappedclass(son)
        else:
            return Document(son)
