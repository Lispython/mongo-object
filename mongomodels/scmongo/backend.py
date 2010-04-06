from svarga.core.env import env
from svarga.models import model
from svarga.core.metadata import create_metadata
from svarga.utils.imports import import_module

import pymongo
from pymongo.son_manipulator import AutoReference, NamespaceInjector
from mongomodels import Model, Manager, MetaModel

class ScManager(Manager, model.BaseModelManager):
    "Mix of managers"
    def __init__(self, model_class):
        self.model_class = model_class

    @property
    def _db(self):
        "_db property return connection from pool"
        return env.mongo_connection

class ScMetaModel(MetaModel):
    "Metaclass for ScMongoModel creation"
    def __new__(cls, classname, bases, fields):
        create_metadata(cls, bases, fields)
        
        model = super(ScMetaModel, cls).__new__(cls, classname, bases, fields)

        model.__table__ = classname
        model.objects = ScManager(model)

        # Process fields
        for field in model._fields.values():
            # Set order in db
            if field.order:
                model.objects.collection.create_index([(field.name, field.order)])
        
        model.Meta.update()

        return model

class ScMongoModel(Model):
    "Model for MongoDB"
    __metaclass__ = ScMetaModel
    _base_model = True

    def save(self):
        self.objects.save(self)

    def delete(self):
        self.objects.delete(self)

class MongoBackend(object):
    "Svarga MongoDB backend"
    name = 'mongo'

    def __init__(self, apps, env_class):
        db_name = getattr(env_class.settings, 'MONGO_DB')
        env_class.mongo_connection = pymongo.Connection()[db_name]
        #env_class.mongo_connection.add_son_manipulator(NamespaceInjector())

        # Try loading models from app's models.py
        for app, config in apps.iteritems():
            app_models = app + '.models'
            try:
                mod = import_module(app_models)
            except ImportError:
                pass

    @classmethod
    def get_factory(cls, prefix=''):
        "Return ScMongoModel as base model class"
        if prefix == None:
            prefix = ''
        return type(prefix+'ScMongoModel', (ScMongoModel, ), {'_prefix': prefix, '_base_model': True})

    def sync_db(self):
        pass

