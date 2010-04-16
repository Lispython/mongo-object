"Define Query class"

import pymongo
from doclist import DocList

def parse_query(kwargs):
    """Parse argument list into mongo query.

    Examples:
        (user='jack')  =>  {'user': 'jack'}
        (comment__user='john') => {'comment.user': 'john'}
        (comment__rating__lt=10) => {'comment.rating': {'$lt': 10}}
        (user__in=[10, 20]) => {'user': {'$in': [10, 20]}}
    """
    def to_oid(v):
        if isinstance(v, list):
            return [pymongo.objectid.ObjectId(i) for i in v]
        else:
            return pymongo.objectid.ObjectId(v)

    q = {}
    # iterate over kwargs and build query dict
    for k, v in kwargs.items():
        if v == None:
            print 'Warning: None value for %s key.' % k
        # handle query operators
        op = k.split('__')[-1]
        if op in ('lte', 'gte', 'lt', 'gt', 'ne', 'in', 'nin', 'all', 'size'):
            k = k.rstrip('__' + op)
            if k == '_id':
                v = to_oid(v)

            v = {'$' + op: v}

        elif k == '_id':
            v = to_oid(v)

        # convert django style notation into dot notation
        key = k.replace('__', '.')
        q[key] = v
    return q


def parse_update(kwargs):
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

    print 'parsed update query', q
    return q


class Query(DocList):
    """Query - implement query atom"""

    def __init__(self, manager, query, **kwargs):
        self._manager = manager
        self._query = query.copy()
        u = parse_query(kwargs)
        for k, v in u.iteritems():
            if k in self._query:
                if isinstance(self._query[k], dict):
                    self._query[k].update(v)
                    continue
            self._query[k] = v

        self._litems = None

    def find(self, **kwargs):
        return Query(self._manager, self._query, **kwargs)

    def remove(self):
        "Remove all objects filtered by query chain"
        self._manager._remove(self._query)

    def update(self, **kwargs):
        "Remove all objects filtered by query chain"
        self._manager._update(self._query, parse_update(kwargs))

    @property
    def query(self):
        return self._query

