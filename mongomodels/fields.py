"Define Field class"

class CompareOp(object):
    "Compare operation representation"
    def __init__(self, name, op, other):
        self.name = name
        self.op = op
        self.other = other

class Field(object):
    "Field object for construct lookups"

    def __init__(self, arg):
        if isinstance(arg, type):
            self.type = arg
        else:
            self.value = arg
            self.type = type(arg)

    def _process_model(self, model):
        if issubclass(self.type, list) and not self.name in model:
            model[self.name] = []
        
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

