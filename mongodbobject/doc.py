from pymongo.dbref import DBRef
from platform import python_version

class Doc(dict):
    """The Doc class represents a single document and its features.
    """
    
    def __init__(self, collection, d):
        """ Init dict, then convert included dicts to Nested.
        All dicts in lists and tuples are converted too.
        """
        dict.__init__(self, d)
        self._collection = collection

        for a, b in self.items():
            if isinstance(b, (list, tuple)):
                dict.__setitem__(self, a, [Doc(self._collection, x) if isinstance(x, dict) else x for x in b])
            else:
                dict.__setitem__(self, a, Doc(self._collection, b) if isinstance(b, dict) else b)

    def __setattr__(self, k, v):
        dict.__setitem__(self, k, v)

    def __delattr__(self, k):
        dict.__delitem__(self, k)

    def __getattribute__(self, k):
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            return dict.__getattribute__(self, k)

    def save(self):
        """Save document to collection. 
        If document is new, set generated ID to document _id.
        """

        self.__dict__['_data']._id = self._db[self._collection].save(self.to_dict())
        
    def delete(self):
        """Remove document from collection if a document id exists.
        """
        
        if '_id' in self:
            return self._db[self._collection].remove({'_id': self._id})
        
    def __repr__(self):
        """String representation of a document.
        """
        
        if not '_id' in self:
            return 'Doc(id=<not_saved>)'
        
        return 'Doc(id={0})'.format(self._id.__str__())

    def _str_id(self):
        return str(self._id)
