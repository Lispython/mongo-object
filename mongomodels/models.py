from pymongo.dbref import DBRef
from errors import DatabaseError
from fields import Field


class MongoModels(object):
    "Singleton class for keep models information"
    models = {}

    @classmethod
    def add(cls, model):
        if model._name in cls.models:
            raise DatabaseError('Model duplications. Use prefix for overide that')
        cls.models[model._name] = model

    @classmethod
    def dereference(cls, db, dbref):
        return cls.models[dbref.collection](db.dereference(dbref))


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

        if isinstance(v, Model):
            return DBRef(v._name, v._id, v._database_name)

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

    def __getattr__(self, k):
        return dict.__getitem__(self, k)

# XXX Seems to work without this
#    def __getattribute__(self, k):
#        print "Invoke Model getattr", k
#        try:
#            return dict.__getitem__(self, k)
#        except KeyError:
#            return dict.__getattribute__(self, k)


class MetaModel(type):
    "Modify Model classes"

    def __new__(mcs, name, bases, dict):
        "Save name of model, prefix, append it to MongoModels."

        base_model = dict.get('_base_model', False) # Save flag
        if base_model:
            del dict['_base_model'] # Clear flag to childs

        # Get fields
        fields = {}
        for k, v in dict.items():
            if isinstance(v, Field):
                v.name = k # set field name
                fields[k] = v
                del dict[k]

        model = type.__new__(mcs, name, bases, dict)
        model._name = model._prefix + '_' + name if model._prefix else name
        model._fields = fields

        # Add to models collection for dereference
        if not base_model:
            MongoModels.add(model) 

        return model

    def __getattribute__(cls, k):
        "Implement for lookup at fields on classes"
        try:
            return type.__getattribute__(cls, k) # Try usual way
        except AttributeError:
            if k in cls._fields: # look to _fields if no success
                return cls._fields[k]
            raise # If not in fields pass exception up


class Model(HandyDict):
    "The Model class represents a single document and its features."
    __metaclass__ = MetaModel
    _database_name = None
    _prefix = '' # prepend collection name
    _base_model = True # base models are not in fact really models
    
    @property
    def id(self):
        return str(self._id)

    def __repr__(self):
        return '%s(%s)' % (self._name, dict.__repr__(self))

