from pymongo.dbref import DBRef

class HandyDict(dict):
    "Smart dict with handy access to dict elements"
    def __init__(self, *args, **kwargs):
        """Init dict, then convert included dicts to BaseDoc.
        All dicts in lists and tuples are converted too."""

        dict.__init__(self, *args, **kwargs)

        for a, b in self.items():
            self._update(a, b)

    def _convert(self, v):
        "Convert value"
        if isinstance(v, list):
            return [self._convert(x) for x in v]
        elif isinstance(v, dict):
            return HandyDict(v)
        return v

    def _update(self, k, v):
        "Convert all dicts in v to HandyDict"
        dict.__setitem__(self, k, self._convert(v))

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
    
    def _convert(self, v):
        "Add DBRef convertion to HandyDict._convert"
        if isinstance(v, Model):
            return DBRef(self._name, v._id)
        else:
            return HandyDict._convert(self, v)

    def id(self):
        return str(self._id)

    def __repr__(self):
        return '%s(%s)' % (self._name, dict.__repr__(self))

