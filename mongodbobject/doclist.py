class DocList(object):
    """Represents a list of documents that are iteratable. 
    Objectifying the documents is lazy. Every doc gets converted to 
    an object if it's requested through the iterator.
    """
    def __init__(self, manager, items):
        """Initialize DocList using the manager it belongs to and
        the items as iterator.
        """
        self._items = items
        self._manager = manager
    
    def __iter__(self):
        """Iterator
        """
        return self
    
    def skip(self, num):
        """Skip 'num' docs starting at the beginning.
        """
        return DocList(self._manager, self._items.skip(num))
        
    def limit(self, num):
        """Limit result list to 'num' docs.
        """
        return DocList(self._manager, self._items.limit(num))
        
    def sort(self, **kwargs):
        """Sort result on key.
        sort(name=1, person__gender=1)  =>  {'name': 1, 'person.gender': 1}
        """
        sort = [(k.replace('__', '.'), v) for k, v in kwargs.items()]
        return DocList(self._manager, self._items.sort(sort))
        
    def __len__(self):
        """Number of results.
        """
        return self.count()
        
    def count(self):
        """Number of results.
        """
        return self._items.count()
    
    def next(self):
        """Iterator
        """
        try:
            return self._manager.model_class(self._items.next())
        except StopIteration:
            raise StopIteration
