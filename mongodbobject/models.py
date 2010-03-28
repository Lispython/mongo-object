from manager import Manager

class HandyDict(dict):
    "Smart dict with handy access to dict elements"
    def __init__(self, *args, **kwargs):
        """Init dict, then convert included dicts to BaseDoc.
        All dicts in lists and tuples are converted too."""

        dict.__init__(self, *args, **kwargs)

        # TODO dont cover all situations
        for a, b in self.items():
            if isinstance(b, (list, tuple)):
                dict.__setitem__(self, a, [HandyDict(x) if isinstance(x, dict) else x for x in b])
            else:
                dict.__setitem__(self, a, HandyDict(b) if isinstance(b, dict) else b)

    def __setattr__(self, k, v):
        dict.__setitem__(self, k, v)

    def __delattr__(self, k):
        dict.__delitem__(self, k)

    def __getattribute__(self, k):
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            return dict.__getattribute__(self, k)

class MetaModel(type):
    def __new__(mcs, name, bases, dict):
        model = type.__new__(mcs, name, bases, dict)
        model._name = name
        return model

class Model(HandyDict):
    "The Doc class represents a single document and its features."
    __metaclass__ = MetaModel
    
    def id(self):
        return str(self._id)

    def __repr__(self):
        return '%s(%s)' % (self._name, dict.__repr__(self))

