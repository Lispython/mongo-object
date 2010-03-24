class Nested(dict):
    """Translates dictionary keys to instance attributes"""

    def __init__(self, *args, **kwargs):
        """ Init dict, then convert included dicts to Nested.
        All dicts in lists and tuples are converted too.
        """
        dict.__init__(self, *args, **kwargs)

        for a, b in self.iteritems():
            if isinstance(b, (list, tuple)):
                dict.__setitem__(self, a, [Nested(x) if isinstance(x, dict) else x for x in b])
            else:
                dict.__setitem__(self, a, Nested(b) if isinstance(b, dict) else b)

    def __setattr__(self, k, v):
        dict.__setitem__(self, k, v)

    def __delattr__(self, k):
        dict.__delitem__(self, k)

    def __getattribute__(self, k):
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            return dict.__getattribute__(self, k)

