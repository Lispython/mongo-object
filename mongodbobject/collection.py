import pymongo
from pymongo.dbref import DBRef
from doc import Doc
from doclist import DocList

# patch DBRef to allow lazy retrieval of referenced docs
def get(self, name):
    return getattr(Doc(self.collection, db[self.collection].find_one(self.id).to_dict()), name)
DBRef.__getattr__ = get

class MetaModel(type):
    def __new__(mcs, name, bases, dict):
        model = type.__new__(mcs, name, bases, dict)
        model._name = name
        return model

class Collection(object):
    """Represents all methods a collection can have. To create a new
    document in a collection, call new().
    """
    __metaclass__ = MetaModel

    @classmethod
    def _db(cls):
        return cls._connection

    @classmethod
    def new(cls, data={}):
        """Return empty document, with preset collection.
        """

        return Doc(cls, data)

    @classmethod
    def _parse_query(cls, kwargs):
        """Parse argument list into mongo query.

        Examples:
            (user='jack')  =>  {'user': 'jack'}
            (comment__user='john') => {'comment.user': 'john'}
            (comment__rating__lt=10) => {'comment.rating': {'$lt': 10}}
            (user__in=[10, 20]) => {'user': {'$in': [10, 20]}}
        """

        q = {}
        # iterate over kwargs and build query dict
        for k, v in kwargs.items():
            # handle query operators
            op = k.split('__')[-1]
            if op in ('lte', 'gte', 'lt', 'gt', 'ne',
                'in', 'nin', 'all', 'size'):
                v = {'$' + op: v}
                k = k.rstrip('__' + op)

            # XXX dunno if we really need this?
            if type(v) == list:
                v = str(v)

            # convert django style notation into dot notation
            key = k.replace('__', '.')
            q[key] = v
        return q

    @classmethod
    def _parse_update(cls, kwargs):
        """Parse update arguments into mongo update dict.

        Examples:
            (name='jack')  =>  {'name': 'jack'}
            (person__gender='male')  =>  {'person.gender': 'male'}
            (set__friends=['mike'])  =>  {'$set': {'friends': ['mike']}}
            (push__friends='john')  =>  {'$push': {'friends': 'john'}}
        """

        q = {}
        op_list = {}
        # iterate over kwargs
        for k, v in kwargs.items():

            # get modification operator
            op = k.split('__')[0]
            if op in ('inc', 'set', 'push', 'pushall', 'pull', 'pullall'):
                # pay attention to case sensitivity
                op = op.replace('pushall', 'pushAll')
                op = op.replace('pullall', 'pullAll')

                # remove operator from key
                k = k.replace(op + '__', '')

                # append values to operator list (group operators)
                if not op_list.has_key(op):
                    op_list[op] = []

                op_list[op].append((k, v))
            # simple value assignment
            else:
                q[k] = v

        # append operator dict to mongo update dict
        for k, v in op_list.items():
            for i in v:
                q['$' + k] = {i[0]: i[1]}

        return q

    @classmethod
    def find_one(cls, **kwargs):
        """Find one single document. Mainly this is used to retrieve
        documents by unique key.
        """

        docs = cls._db()[self._name].find_one(cls._parse_query(kwargs))

        if docs is None:
            return None

        return Doc(self, docs.to_dict())

    @classmethod
    def query(cls, **kwargs):
        """This method is used to first say which documents should be
        affected and later what to do with these documents. They can be
        removed or updated after they have been selected.

        c = Collection('test')
        c.query(name='jack').delete()
        c.query(name='jack').update(set__name='john')
        """

        class RemoveUpdateHandler(Collection):
            def __init__(self, collection, query):
                self._db = collection._db()
                self._collection = collection._name
                self.__query = query

            def remove(self):
                self._db()[self._collection].remove(self.__query)

            def update(self, **kwargs):
                self._db()[self._collection].update(
                    self.__query,
                    self._parse_update(kwargs)
                )

        # return handler
        return RemoveUpdateHandler(cls, cls._parse_query(kwargs))

    @classmethod
    def find(cls, **kwargs):
        """Find documents based on query using the django query syntax.
        See _parse_query() for details.
        """

        return DocList(
            cls,
            cls._db()[cls._name].find(cls._parse_query(kwargs))
        )

    @classmethod
    def find_one(cls, **kwargs):
        """Find one single document. Mainly this is used to retrieve
        documents by unique key.
        """

        if '_id' in kwargs:
            args = pymongo.objectid.ObjectId(str(kwargs['_id']))
        else:
            args = cls._parse_query(kwargs)

        docs = cls._db()[cls._name].find_one(args)

        if docs is None:
            return None

        return Doc(cls, docs)
