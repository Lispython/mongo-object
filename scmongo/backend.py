from svarga.core.env import env
from svarga.models import model
from svarga.core.metadata import create_metadata
import pymongo
from mongodbobject import Model, Manager
from mongodbobject.models import MetaModel

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
        
        model = type.__new__(cls, classname, bases, fields)
        model._name = classname
        model.__table__ = classname
        model.objects = ScManager(model)

        return model

class ScMongoModel(Model):
    "Model for MongoDB"
    __metaclass__ = ScMetaModel

class MongoBackend(object):
    name = 'mongo'

    def __init__(self, apps, env_class):
        db_name = getattr(env_class.settings, 'MONGO_DB')
        env_class.mongo_connection = pymongo.Connection()[db_name]

    @classmethod
    def get_factory(cls, prefix):
        "Return ScMongoModel as base model class"
        return ScMongoModel

    def sync_db(self):
        pass

