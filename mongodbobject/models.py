from manager import Manager

class HandyDict(dict):
    "Smart dict with handy access to dict elements"
    def __init__(self, *args, **kwargs):
        """Init dict, then convert included dicts to BaseDoc.
        All dicts in lists and tuples are converted too."""

        dict.__init__(self, *args, **kwargs)

        for a, b in self.items():
            self._update(a, b)

    def _update(self, k, v):
        "Convert all dicts in v to HandyDict"
        # TODO doesnt cover all situations
        if isinstance(v, (list, tuple)):
            dict.__setitem__(self, k, [HandyDict(x) if isinstance(x, dict) else x for x in v])
        else:
            dict.__setitem__(self, k, HandyDict(v) if isinstance(v, dict) else v)

    def __setattr__(self, k, v):
        self._update(k, v)

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

