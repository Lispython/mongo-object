# -*- coding:  utf-8 -*-

import pymongo
import unittest
from mongodbobject import *

class User(Model):

    def upper_name(self):
        return  self.name.upper()

class TestMongoModels(unittest.TestCase):
    def setUp(self):
        self.test_dict = {
            u'me': {u'age': 24, u'gender': u'male'},
            u'name': u'john',
            u'friends': [u'mike', u'dwight', u'elliot'],
            }
        self.collection = pymongo.Connection().mongoobject_test_collection

    def tearDown(self):
        pass
        
    def testDocumentMethods(self):
        manager = Manager(self.collection, User)
        document = User(name = self.test_dict['name'])
        document.me = self.test_dict['me']
        document.friends = self.test_dict['friends']
        self.assertEquals(document.name, self.test_dict['name'])
        self.assertEquals(document.me, self.test_dict['me'])
        self.assertEquals(document.friends, self.test_dict['friends'])
        self.assertEquals(document.me.gender, self.test_dict['me']['gender'])
        _id = manager.save(document)
        self.assertEquals(document._id, _id)
        document2 = manager.find_one(me__age=24)
        self.assertEqual(document.me.gender, document2.me.gender)
        #self.assertEqual(str(document._id), str(document2._id))
        self.assertEqual(document.upper_name(), self.test_dict['name'].upper())


if __name__ == '__main__':
    unittest.main()
