import pymongo
from doclist import DocList
from models import MongoModels
from query import parse_update, parse_query

class Manager(object):
    """Represents all methods a collection can have. To create a new
    document in a collection, call new().
    """
    def __init__(self, connection, model_or_class):
        "Store db connection and model or model class"
        if isinstance(model_or_class, type):
            self.model_class = model_or_class
            self.model = None
        else:
            self.model_class = model_or_class.__class__
            self.model = model_or_class

        self._db = connection
        
    def query(self, **kwargs):
        """This method is used to first say which documents should be
        affected and later what to do with these documents. They can be
        removed or updated after they have been selected.

        c = Collection('test')
        c.query(name='jack').delete()
        c.query(name='jack').update(set__name='john')
        """

        class RemoveUpdateHandler(Manager):
            def __init__(self, manager, query):
                self.manager = manager
                self.model_class = manager.model_class
                self.__query = query

            def remove(self):
                self.manager._db[self.model_class._name].remove(self.__query)

            def update(self, **kwargs):
                self.manager._db[self.model_class._name].update(
                    self.__query,
                    parse_update(kwargs)
                )

        # return handler
        return RemoveUpdateHandler(self, parse_query(kwargs))

    def find(self, **kwargs):
        """Find documents based on query using the django query syntax.
        See parse_query() for details.
        """

        return DocList(
            self,
            self._db[self.model_class._name].find(parse_query(kwargs))
        )

    def find_one(self, **kwargs):
        """Find one single document. Mainly this is used to retrieve
        documents by unique key.
        """

        if '_id' in kwargs:
            args = pymongo.objectid.ObjectId(str(kwargs['_id']))
        else:
            args = parse_query(kwargs)

        docs = self._db[self.model_class._name].find_one(args)

        if docs is None:
            return None

        return self.model_class(docs)

    def save(self, model):
        """Save document to collection. 
        If document is new, set generated ID to document _id.
        """
        model._id = self._db[self.model_class._name].save(model)
        return model._id
        
    def delete(self, model):
        "Remove document from collection if a document id exists."
        if '_id' in model:
            self._db[self.model_class._name].remove({'_id': model._id})
            del model['_id']

    def dereference(self, dbref):
        return MongoModels.dereference(self._db, dbref) 

    # Aliases        
    def add(self, model):
        return self.save(model)

    def all(self):
        return self.find()

    def get(self, **kwargs):
        return self.find_one(**kwargs)

    def filter_by(self, **kwargs):
        return self.find(**kwargs)

