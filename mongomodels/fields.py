"Define Field class"

import pymongo

class CompareOp(object):
    "Compare operation representation"
    def __init__(self, name, op, other):
        self.name = name
        self.op = op
        self.other = other

class Field(object):
    "Field object for construct lookups"
    ASCENDING = pymongo.ASCENDING
    DESCENDING = pymongo.DESCENDING

    def __init__(self, arg, default=None, order=None):
        if isinstance(arg, type):
            self.type = arg
        else:
            self.value = arg
            self.type = type(arg)
        self.default = default
        self.order = order

    def process_model(self, model):
        # Set field default value
        if self.default != None and not self.name in model:
            model[self.name] = self.default

    def __lt__(self, other):
        return CompareOp(self.name, '<', other)

    def __le__(self, other):
        return CompareOp(self.name, '<=', other)

    def __eq__(self, other):
        return CompareOp(self.name, '=', other)

    def __ne__(self, other):
        return CompareOp(self.name, '!=', other)

    def __gt__(self, other):
        return CompareOp(self.name, '>', other)

    def __ge__(self, other):
        return CompareOp(self.name, '>=', other)


